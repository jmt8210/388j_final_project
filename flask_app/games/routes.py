from flask import Blueprint, render_template, request, redirect, url_for, send_file, flash, get_flashed_messages
from PIL import Image, ImageDraw
import base64
from io import BytesIO
from flask_login import (
  current_user,
  login_required,
  login_user,
  logout_user
)
from ..models import User, Game, load_user
from ..forms import (
  LoginForm,
  RegistrationForm,
  CreateGameForm
)
# from .. import bcrypt

games = Blueprint("games", __name__)

@games.route('/play')
@login_required
def play():
  return render_template('account.html')


@games.route("/create_game", methods=['GET', 'POST'])
@login_required
def create_game():
  form = CreateGameForm()
  if form.validate_on_submit():
    id = len(Game.objects())
    game = Game(user_one=current_user.username, user_two=form.username.data, game_id=id, user_turn=2, game_data=[])
    game.save()
    return redirect(url_for('users.account'))
  return render_template('create_game.html', current_user=current_user, form=form)

@games.route('/game/<game_id>')
@login_required
def game(game_id):
  game = Game.objects(game_id=game_id).first()
  game_data = list(game.game_data)
  is_user_turn = False
  if (game.user_turn == 1 and game.user_one == current_user.username) or (game.user_turn == 2 and game.user_two == current_user.username):
    is_user_turn = True
  print(is_user_turn)
  opp = game.user_one if game.user_one != current_user.username else game.user_two
  args = request.args.to_dict()
  cell = -1
  if 'cell' in args:
    cell = int(args['cell'])
    game_data.append(cell)
  board_img = draw_game(game_data)

  return render_template('game.html', board_img=board_img, game=game, cell=cell, is_user_turn=is_user_turn, opp=opp)

@games.route('/update_game/<game_id>/<cell>')
def update_game(game_id, cell):
  game = Game.objects(game_id=game_id).first()
  game_data = list(game.game_data)
  game_data.append(int(cell))
  if check_win(game_data):
    game.modify(game_data=game_data, user_turn=0, winner=current_user.username)
  else:
    user_turn = 1
    if game.user_turn == 1:
      user_turn = 2
    game.modify(game_data=game_data, user_turn=user_turn)
  return redirect(url_for('games.game', game_id=game_id))

@games.route('/get_game_img/<game_id>')
def get_game_img(game_id):
  headers = {
        'Content-Type': 'image/jpeg',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0' # Expire immediately, so browser has to reverify everytime
    }
  game = Game.objects(game_id=game_id).first()
  game_data = list(game.game_data)
  return draw_game_to_buffer(game_data).getvalue(), headers

def draw_game_to_buffer(game_data):
  image = Image.new("RGB", (440, 440), "white")
  draw = ImageDraw.Draw(image)
  draw_tic_tac_template(draw)
  if len(game_data) > 0:
    draw_game_data(draw, game_data)
  buffered = BytesIO()
  image.save(buffered, format="JPEG", quality=100)
  return buffered

def draw_game(game_data):
  buffered = draw_game_to_buffer(game_data)
  board_img = base64.b64encode(buffered.getvalue()).decode()
  return board_img

# Drawing Functions

def draw_tic_tac_template(draw):
  draw.rounded_rectangle((140, 0, 150, 440), fill=(200, 200, 200), radius=10)
  draw.rounded_rectangle((290, 0, 300, 440), fill=(200, 200, 200), radius=10)
  draw.rounded_rectangle((0, 140, 440, 150), fill=(200, 200, 200), radius=10)
  draw.rounded_rectangle((0, 290, 440, 300), fill=(200, 200, 200), radius=10)

def draw_game_data(draw, game_data):
  for i in range(len(game_data)):
    x = game_data[i] % 3
    y = int(game_data[i] / 3)
    draw_x(draw, x, y) if i % 2 == 0 else draw_o(draw, x, y)
  win_line = find_three_in_a_row(game_data)
  if win_line != []:
    draw_win(draw, win_line[0], win_line[1])

def draw_x(draw, x, y):
  size = 30
  x_fixed = x * 140 + 10 * x + 70
  y_fixed = y * 140 + 10 * y + 70
  draw.line((x_fixed - size, y_fixed - size, x_fixed + size, y_fixed + size), fill=(255, 0, 0), width=7)
  draw.line((x_fixed - size, y_fixed + size, x_fixed + size, y_fixed - size), fill=(255, 0, 0), width=7)

def draw_o(draw, x, y):
  size = 35
  x_fixed = x * 140 + 10 * x + 70
  y_fixed = y * 140 + 10 * y + 70
  draw.ellipse((x_fixed - size, y_fixed - size, x_fixed + size, y_fixed + size), outline=(0, 0, 255), width=7)

def draw_win(draw, cell1, cell2):
  cell1_x = (cell1 % 3) * 140 + 10 * (cell1 % 3) + 70
  cell1_y = (int(cell1 / 3)) * 140 + 10 * (int(cell1 / 3)) + 70
  cell2_x = (cell2 % 3) * 140 + 10 * (cell2 % 3) + 70
  cell2_y = (int(cell2 / 3)) * 140 + 10 * (int(cell2 / 3)) + 70
  draw.line((cell1_x, cell1_y, cell2_x, cell2_y), fill=(0, 255, 0), width=10)

def draw_logo():
  image1 = Image.open('logo.png')
  image = image1.convert("RGBA")
  datas = image.getdata()
  newData = []
  for item in datas:
   if item[0] == 0 and item[1] == 0 and item[2] == 0:
    newData.append((255, 255, 255, 0))
   else:
    newData.append(item)
  image.putdata(newData)

  draw = ImageDraw.Draw(image)
  size = 30
  x_fixed = 35
  y_fixed = 35
  draw.line((x_fixed - size, y_fixed - size, x_fixed + size, y_fixed + size), fill=(255, 0, 0), width=7)
  draw.line((x_fixed - size, y_fixed + size, x_fixed + size, y_fixed - size), fill=(255, 0, 0), width=7)
  size = 35
  draw.ellipse((x_fixed - size, y_fixed - size, x_fixed + size, y_fixed + size), outline=(0, 0, 255), width=7)
  image.save("logo.png", quality=100)

def find_three_in_a_row(game_data):
  one_moves = [0 for _ in range(9)]
  two_moves = [0 for _ in range(9)]
  for i in range(len(game_data)):
    two_moves[game_data[i]] = 1 if i % 2 == 0 else one_moves[game_data[i]]

  # Check horizontal
  for i in range(3):
    if one_moves[i*3] == 1 and one_moves[i*3 + 1] == 1 and one_moves[i*3 + 2] == 1:
      return [i*3, i*3 + 2]

  for i in range(3):
    if two_moves[i*3] == 1 and two_moves[i*3 + 1] == 1 and two_moves[i*3 + 2] == 1:
      return [i*3, i*3 + 2]

  # Check vertical
  for i in range(3):
    if one_moves[i] == 1 and one_moves[i+3] == 1 and one_moves[i+6] == 1:
      return [i, i + 6]

  for i in range(3):
    if two_moves[i] == 1 and two_moves[i+3] == 1 and two_moves[i+6] == 1:
      return [i, i + 6]

  # Check diagonals
  if one_moves[0] == 1 and one_moves[4] == 1 and one_moves[8] == 1:
    return [0, 8]
  if one_moves[6] == 1 and one_moves[4] == 1 and one_moves[2] == 1:
    return [6, 2]
  if two_moves[0] == 1 and two_moves[4] == 1 and two_moves[8] == 1:
    return [0, 8]
  if two_moves[6] == 1 and two_moves[4] == 1 and two_moves[2] == 1:
    return [6, 2]

  # No winner found
  return []



  

def check_win(game_data):
  if find_three_in_a_row(game_data) != []:
    return True
  return False
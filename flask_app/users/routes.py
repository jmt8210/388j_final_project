from flask import Blueprint, render_template, request, redirect, url_for, flash, get_flashed_messages
from flask_login import (
  current_user,
  login_required,
  login_user,
  logout_user
)
from ..models import User, Game, load_user
from ..forms import (
  LoginForm,
  RegistrationForm
)
from .. import bcrypt


users = Blueprint("users", __name__)

@users.route('/')
def index():
  games = list(Game.objects())
  return render_template('index.html', games=games)

@users.route("/register", methods=["GET", "POST"])
def register():
  if current_user.is_authenticated:
    return redirect(url_for('users.index'))

  form = RegistrationForm()
  if form.validate_on_submit():
    hashed = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
    user = User(username=form.username.data, password=hashed)
    user.save()
    return redirect(url_for('users.login'))
  return render_template("register.html", form=form)

@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
      return redirect(url_for('users.account'))
    form = LoginForm()
    if form.validate_on_submit():
      user = User.objects(username=form.username.data).first()
      if (user is not None and bcrypt.check_password_hash(user.password, form.password.data)):
        login_user(user)
        return redirect(url_for('users.account'))
      else:
        flash('Login failed, please try again')
    return render_template('login.html', current_user=current_user, form=form)

@users.route('/account')
@login_required
def account():
  games1 = list(Game.objects(user_one=current_user.username))
  games2 = list(Game.objects(user_two=current_user.username))
  games = []
  gameids = []
  for i in games1:
    games.append(i)
    gameids.append(i.game_id)
  for i in games2:
    if i.game_id not in gameids:
      games.append(i)
  return render_template('account.html', games=games)

@users.route('/logout')
@login_required
def logout():
  logout_user()
  return redirect(url_for('users.index'))
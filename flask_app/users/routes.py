from threading import currentThread
from flask import Blueprint, render_template, request, redirect, url_for, flash, get_flashed_messages
from flask_login import (
  current_user,
  login_required,
  login_user,
  logout_user
)
from ..models import User, Game, Comment, load_user
from ..forms import (
  CreateGameComment,
  LoginForm,
  RegistrationForm,
  UpdateUsernameForm
)
from .. import bcrypt
from datetime import datetime


users = Blueprint("users", __name__)

@users.route('/')
def index():
  if current_user.is_authenticated:
    return redirect(url_for('users.feed'))
  games = list(Game.objects())
  comments = list(Comment.objects())
  return render_template('index.html', games=games, comments=comments)

@users.route('/feed', methods=['GET', 'POST'])
@login_required
def feed():
  games = list(Game.objects())
  for g in games:
    g.form = CreateGameComment(prefix=str(g.game_id))
    if g.form.data['submit'] and g.form.validate():
      comment = Comment(username=current_user.username, comment=g.form.comment.data, date=datetime.now(), game_id=g.game_id)
      comment.save()
      return redirect(url_for('users.feed'))
  comments = list(Comment.objects())
  return render_template('feed.html', games=games, comments=comments)

@users.route("/register", methods=["GET", "POST"])
def register():
  if current_user.is_authenticated:
    return redirect(url_for('users.index'))

  form = RegistrationForm()
  if form.validate_on_submit():
    hashed = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
    user = User(username=form.username.data.lower(), password=hashed)
    user.save()
    return redirect(url_for('users.login'))
  return render_template("register.html", form=form)

@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
      return redirect(url_for('users.account'))
    form = LoginForm()
    if form.validate_on_submit():
      user = User.objects(username=form.username.data.lower()).first()
      if (user is not None and bcrypt.check_password_hash(user.password, form.password.data)):
        login_user(user)
        return redirect(url_for('users.account'))
      else:
        flash('Login failed, please try again')
    return render_template('login.html', current_user=current_user, form=form)

@users.route('/account', methods=['GET', 'POST'])
@login_required
def account():
  username_form = UpdateUsernameForm()
  user = load_user(current_user.get_id())
  if username_form.submit_username.data and username_form.validate():
      username = username_form.username.data.lower()
      user.modify(username=username)
      return redirect(url_for('users.account'))
  return render_template('account.html', username_form=username_form)

@users.route('/logout')
@login_required
def logout():
  logout_user()
  return redirect(url_for('users.index'))
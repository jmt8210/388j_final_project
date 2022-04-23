from flask import render_template, request, redirect, url_for, flash, get_flashed_messages
from flask_login import (
  current_user,
  login_required,
  login_user,
  logout_user
)
from .models import User, load_user
from .forms import (
  LoginForm,
  RegistrationForm
)
from . import app, bcrypt

@app.route('/')
def index():
  return render_template('index.html')

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, password=hashed)
        user.save()
        return redirect(url_for('login'))
    return render_template("register.html", form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('account'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.objects(username=form.username.data).first()
        if (user is not None and bcrypt.check_password_hash(user.password, form.password.data)):
            login_user(user)
            return redirect(url_for('account'))
        else:
            flash('Login failed, please try again')
    return render_template('login.html', current_user=current_user, form=form)

@app.route('/account')
@login_required
def account():
  return render_template('account.html')

@app.route('/logout')
@login_required
def logout():
  logout_user()
  return redirect(url_for('index'))
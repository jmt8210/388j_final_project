from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import (
    InputRequired,
    Length,
    EqualTo,
    ValidationError,
)

from .models import User

class RegistrationForm(FlaskForm):
    username = StringField(
        "Username", validators=[InputRequired(), Length(min=1, max=40)]
    )
    password = PasswordField("Password", validators=[InputRequired(), Length(min=8)])
    confirm_password = PasswordField(
        "Confirm Password", validators=[InputRequired(), EqualTo("password")]
    )
    submit = SubmitField("Sign Up")

    def validate_username(self, username):
        user = User.objects(username=username.data.lower()).first()
        if user is not None:
            raise ValidationError("Username is taken")

    def validate_password(self, password):
        if not any(char.isdigit() for char in password.data):
            raise ValidationError("Password must have at least one number")
        if not any(char.isupper() for char in password.data):
            raise ValidationError("Password must have at least one uppercase letter")
        if not any(char.islower() for char in password.data):
            raise ValidationError("Password must have at least one lowercase letter")
        if not any(char in "!@#$%^&*()_+=-" for char in password.data):
            raise ValidationError("Password must have at least one special character")


class LoginForm(FlaskForm):
    username = StringField(
        "Username", validators=[InputRequired(), Length(min=1, max=40)]
    )
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Log In")

    def validate_username(self, username):
        user = User.objects(username=username.data.lower()).first()
        if user is None:
            raise ValidationError("Username not found, please create an account")

class UpdateUserInfo(FlaskForm):
    username = StringField(
        "Username", validators=[InputRequired(), Length(min=1, max=40)]
    )
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Log In")

    def validate_username(self, username):
        user = User.objects(username=username.data.lower()).first()
        if user is None:
            raise ValidationError("Username not found, please create an account")

class CreateGameForm(FlaskForm):
    username = StringField(
        "Username", validators=[InputRequired(), Length(min=1, max=40)]
    )
    submit = SubmitField("Send Game Invitation")

    def validate_username(self, username):
        user = User.objects(username=username.data.lower()).first()
        if user is None:
            raise ValidationError("Username not found, please provide a valid username")

class CreateGameComment(FlaskForm):
    comment = StringField("Comment", validators=[InputRequired(), Length(min=1, max=200)])
    submit = SubmitField("Create Comment")

class UpdateUsernameForm(FlaskForm):
    username = StringField(
        "Username", validators=[InputRequired(), Length(min=1, max=40)]
    )
    submit_username = SubmitField("Update Username")

    def validate_username(self, username):
        user = User.objects(username=username.data.lower()).first()
        if user is not None:
            raise ValidationError("Username is taken")
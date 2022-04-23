from flask_login import UserMixin
from . import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    user = User.objects(username=user_id).first()
    return user

class User(db.Document, UserMixin):
  username = db.StringField(unique=True, required=True)
  password = db.StringField(required=True)
  game_ids = db.ListField(required=False)

  def get_id(self):
      return self.username

class Game(db.Document):
  game_id = db.IntField(required=True)
  # accepted = db.BooleanField(required=True)
  user_turn = db.IntField(required=True)
  user_one = db.StringField(required=True)
  user_two = db.StringField(required=True)
  game_data = db.ListField()
  winner = db.StringField()

  def get_id(self):
      return self.id
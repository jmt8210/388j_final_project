# import os

# from flask import Flask
# from flask_mongoengine import MongoEngine
# from flask_login import LoginManager

# from flask_bcrypt import Bcrypt

# from werkzeug.utils import secure_filename


# app = Flask(__name__)
# app.config["MONGODB_HOST"] = "mongodb://localhost:27017/thoms_final_project"
# app.config["SECRET_KEY"] = os.urandom(16)

# app.config.update(
#     SESSION_COOKIE_HTTPONLY=True,
#     SESSION_COOKIE_SAMESITE="Lax",
# )

# db = MongoEngine(app)
# login_manager = LoginManager(app)
# login_manager.login_view = "login"
# bcrypt = Bcrypt(app)

# app.register_blueprint(users)

# def b_64_enc(image_data):
#     bytes_im = io.BytesIO(image_data.read())
#     image = base64.b64encode(bytes_im.getvalue()).decode()
#     return image

# app.jinja_env.globals.update(b_64_enc=b_64_enc)

# login_manager.login_message = "You need to be logged in to view this page."

# from . import routes



# 3rd-party packages
from flask import Flask, render_template, request, redirect, url_for
from flask_mongoengine import MongoEngine
from flask_login import (
    LoginManager,
    current_user,
    login_user,
    logout_user,
    login_required,
)
from flask_bcrypt import Bcrypt
from flask_talisman import Talisman
from werkzeug.utils import secure_filename

# stdlib
from datetime import datetime
import os

# local
# from .client import MovieClient




db = MongoEngine()
login_manager = LoginManager()
bcrypt = Bcrypt()
# movie_client = MovieClient(os.environ.get("OMDB_API_KEY"))

from .games.routes import games
from .users.routes import users
from .info.routes import info


def page_not_found(e):
    return render_template("404.html"), 404


def create_app(test_config=None):
    app = Flask(__name__)

    csp = {
        'default-src': "'self'",
        'img-src': "'self' data:",
        'style-src': "'self' 'unsafe-inline' stackpath.bootstrapcdn.com",
        'script-src': "code.jquery.com stackpath.bootstrapcdn.com cdn.jsdelivr.net"
    }
    Talisman(app, content_security_policy=csp)

    app.config.from_pyfile("config.py", silent=False)
    if test_config is not None:
        app.config.update(test_config)

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    app.register_blueprint(games)
    app.register_blueprint(users)
    app.register_blueprint(info)
    app.register_error_handler(404, page_not_found)

    login_manager.login_view = "users.login"

    return app

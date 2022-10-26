from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
Migrate(app, db)

login = LoginManager()
login.init_app(app)
login.login_view = "login"

from myproject import models, handler
from myproject.users.views import users
from myproject.posts.views import posts
from myproject.core.views import core
from myproject.chats.views import chats

app.register_blueprint(users, url_prefix="/user")
app.register_blueprint(posts, url_prefix="/post")
app.register_blueprint(core) 
app.register_blueprint(chats, url_prefix="/chat") 
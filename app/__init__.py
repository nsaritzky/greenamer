from flask import Flask
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from stravalib import Client
from flask_login import LoginManager

from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bootstrap = Bootstrap(app)
login_manager = LoginManager(app)
login_manager.login_view = 'index'

# Get Strava Oauth URL
client = Client()
OAUTH_URL = client.authorization_url(client_id=Config.CLIENT_ID, redirect_uri=(Config.EXTERNAL_URL + '/auth'),
                                     scope='write')

from app import routes, models

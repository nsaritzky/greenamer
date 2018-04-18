from flask import Flask
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bootstrap = Bootstrap(app)
login_manager = LoginManager(app)
login_manager.login_view = 'index'

from app.webhooks import bp as webhooks_bp
app.register_blueprint(webhooks_bp)

from app import routes, models

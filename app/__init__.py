from flask import Flask
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from config import Config

db = SQLAlchemy()
migrate = Migrate()
bootstrap = Bootstrap()
login = LoginManager()
login.login_view = 'index'


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    bootstrap.init_app(app)

    from app.webhooks import bp as webhooks_bp
    app.register_blueprint(webhooks_bp)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    return app

from app import models
from app.main import routes

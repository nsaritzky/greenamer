import logging
import os
from logging.handlers import RotatingFileHandler
# from flask_cdn import CDN

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_googlemaps import GoogleMaps
from dotenv import load_dotenv

from config import Config

db = SQLAlchemy()
migrate = Migrate()
bootstrap = Bootstrap()
login = LoginManager()
login.login_view = 'main.index'

# cdn = CDN()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    # cdn.init_app(app)
    if not app.config['CDN_DOMAIN']:
        logging.warning('CDN_DOMAIN not set')

    load_dotenv()

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    bootstrap.init_app(app)
    # GoogleMaps(app)

    from app.webhooks import bp as webhooks_bp
    app.register_blueprint(webhooks_bp)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    # from app.maps import bp as maps_bp
    # app.register_blueprint(maps_bp)

    if app.config['LOG_TO_STDOUT']:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        app.logger.addHandler(stream_handler)
    else:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/greenamer.log',
                                           maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.DEBUG)
        app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Greenamer startup')

    return app

from app import models
from app.main import routes

import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    CLIENT_ID = 24713
    CLIENT_SECRET = os.getenv('CLIENT_SECRET')
    WEBHOOK_TOKEN = os.getenv('WEBHOOK_TOKEN')
    EXTERNAL_URL = os.getenv('EXTERNAL_URL')
    OAUTH_URL = 'https://www.strava.com/oauth/authorize?client_id=24713&response_type=code&redirect_uri={0}:5000/auth'.format(
        EXTERNAL_URL)
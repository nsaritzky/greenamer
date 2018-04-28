import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TESTING = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    CLIENT_ID = 24713
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
    S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET')
    STATIC_URL = os.getenv('STATIC_URL')
    WEBHOOK_TOKEN = os.getenv('WEBHOOK_TOKEN')
    SERVER_NAME = os.getenv('SERVER_NAME')
    if SERVER_NAME is not None:
        redirect_url = 'https://' + SERVER_NAME
    else:
        redirect_url = 'http://localhost:5000'
    OAUTH_URL = 'https://www.strava.com/oauth/authorize?client_id=24713&scope=write&response_type=code' \
                '&redirect_uri={0}/auth'.format(redirect_url)
    CDN_DOMAIN = os.getenv('CDN_DOMAIN')
    CDN_TIMESTAMP = False
    GOOGLEMAPS_KEY = os.getenv('GOOGLE_MAPS_KEY')

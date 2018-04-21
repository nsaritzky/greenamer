from datetime import datetime

from geopy.geocoders import Nominatim
from stravalib import Client
from app.models import User, Rule
from flask_login import current_user

from app import db
from config import Config


# def record_new_user(code):
#     client = Client()
#
#     token = client.exchange_code_for_token(client_id=Config.CLIENT_ID,
#                                            client_secret=Config.CLIENT_SECRET,
#                                            code=code)
#     client = Client(access_token=token)
#     athlete = client.get_athlete()
#
#     db.session.add(User(strava_id=athlete.id, access_token=token))
#     db.session.commit()



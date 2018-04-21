from stravalib.exc import AccessUnauthorized

from app import db, login
from flask_login import UserMixin
from stravalib import Client

from config import Config
from flask import url_for, current_app
from datetime import datetime, timedelta
from geopy.distance import distance
from geopy.geocoders import Nominatim
import requests
import logging


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    access_token = db.Column(db.String(128))
    first_name = db.Column(db.String)
    rules = db.relationship('Rule', backref='user', lazy='dynamic')

    @staticmethod
    def subscribe():
        payload = {'client_id' : Config.CLIENT_ID,
                   'client_secret' : Config.CLIENT_SECRET,
                   'callback_url' : 'http://ec2-13-58-76-233.us-east-2.compute.amazonaws.com:5000/handler',
                   'verify_token' : Config.WEBHOOK_TOKEN}
        requests.post('https://api.strava.com/api/v3/push_subscriptions', data = payload)
        # Client.create_subscription(self.id, client_id=Config.CLIENT_ID, client_secret=Config.CLIENT_SECRET,
        #                            callback_url='http://ec2-13-58-76-233.us-east-2.compute.amazonaws.com:5000/handler', verify_token=Config.WEBHOOK_TOKEN)

    def make_rule(self, address: str, day_and_time: datetime, activity_name: str):
        geolocator = Nominatim(timeout=10)
        location = geolocator.geocode(address)
        new_rule = Rule(lat=location.latitude, lng=location.longitude,
                        address=address, time=day_and_time, user_id=self.id,
                        activity_name=activity_name)
        db.session.add(new_rule)
        db.session.commit()
        logging.info('New rule added: {}'.format(new_rule))

    def resolve_webhook(self, object_id: int) -> str:
        client = Client(access_token=self.access_token)
        activity = client.get_activity(object_id)
        # The Strava API doesn't give enough precision in its start latitude and longitude values, so we have
        # to call the raw stream of points to get what we need.
        points = client.get_activity_streams(activity.id, types=['latlng'], resolution='low')
        activity_start = points['latlng'].data[0]
        logging.debug('Webhook event received: Activity {}, User {}, Starting point {}, Starting time {}'.format(
            object_id, self.id, activity_start, activity.start_date_local))
        # TODO: If any of the rules for the user overlap, this check will just go with whichever one it happens to
        # finds first. That's probably not a great way to do it.
        for rule in self.rules.all():
            logging.debug('Checking {} against activity {}'.format(rule, object_id))
            if rule.check_rule(activity_start, activity.start_date_local):
                if not current_app.config.TESTING:
                    client.update_activity(object_id, name=rule.activity_name)
                logging.info('Activity {} renamed to {} for {}'.format(activity.id, rule.activity_name, self))
                return rule.activity_name
        return ''

    def __repr__(self):
        return '<User {}; First Name: {}>'.format(self.id, self.first_name)


class Rule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)  # The latitude and longitude associated to the rule are computed on creation
    address = db.Column(db.String)  # The address is stored for display back to the user
    time = db.Column(db.DateTime)
    append_date = db.Column(db.Boolean)
    activity_name = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # Checks if a given timestamp (in units of seconds from Epoch) is within 1,000 seconds of the time specified
    # in the rule, modulo 1 week
    def check_time(self, start_time: datetime, delta=timedelta(seconds=1000)) -> bool:
        week: timedelta = timedelta(days=7)
        difference = start_time - self.time
        return ((difference % week) < delta) or ((-difference % week) < delta)

    def check_distance(self, start_point, radius: float = .25) -> bool:
        rule_point = (self.lat, self.lng)
        return distance(start_point, rule_point).miles < radius

    # The time and distance checks are being kept separate mostly for unit tests, but most of the time, they're used
    # together. So here's a function that combines them.
    def check_rule(self, start_point, start_time: datetime, delta=timedelta(seconds=1000), radius: float = .25) -> bool:
        return self.check_time(start_time, delta) and self.check_distance(start_point, radius)

    def __repr__(self):
        return '<Location: ({}, {}), Title: {}, User: {}>'.format(self.lat, self.lng, self.activity_name, self.user_id)


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

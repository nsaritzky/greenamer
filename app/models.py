from app import db, login_manager
from flask_login import UserMixin
from stravalib import Client
from config import Config
from flask import url_for
from datetime import datetime, timedelta
from geopy.distance import distance
from geopy.geocoders import Nominatim
import logging


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    access_token = db.Column(db.String(128))
    first_name = db.Column(db.String)
    rules = db.relationship('Rule', backref='user', lazy='dynamic')

    def subscribe(self):
        Client.create_subscription(self.id, client_id=Config.CLIENT_ID, client_secret=Config.CLIENT_SECRET,
                                   callback_url=url_for('webhook_handler'))

    def make_rule(self, address: str, day_and_time: datetime, activity_name: str):
        geolocator = Nominatim(timeout=10)
        location = geolocator.geocode(address)
        new_rule = Rule(lat=location.latitude, lng=location.longitude,
                        address=address, time=day_and_time, user_id=self.id,
                        activity_name=activity_name)
        db.session.add(new_rule)
        db.session.commit()
        logging.info('New rule added: {}'.format(new_rule))

    def resolve_webhook(self, object_id: int):
        client = Client(access_token=self.access_token)
        activity = client.get_activity(activity_id=object_id)
        for rule in self.rules.all():
            if rule.check_time(start_time=activity.start_date_local) and rule.check_distance(start_point=(
                    activity.start_longitude, activity.start_latitude)):
                client.update_activity(name=rule.activity_name)
                logging.info('Activity {} renamed to {} for {}'.format(activity.id, rule.activity_name, self))

    def __repr__(self):
        return '<User {}>'.format(self.id)


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

    def __repr__(self):
        return 'Location: ({}, {}), Title: {}, User: {}'.format(self.lat, self.lng, self.activity_name, self.user_id)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

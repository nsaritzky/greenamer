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


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)  # The user's Strava ID
    access_token = db.Column(db.String(128))  # Strava access token
    refresh_token = db.Column(db.String(128))  # Strava refresh token
    access_expr = db.Column(db.DateTime)
    first_name = db.Column(db.String)  # First name, pulled from Strava
    rules = db.relationship("Rule", backref="user", lazy="dynamic")

    @staticmethod
    def add_user(code: str):
        """
        Takes a temporary access code returned from Strava and retrieves the
        associated user and access token. Then it checks for the user in the
        database. If they're not found, then the new user is recorded. If they are
        found, then just the access token is recorded in case it has changed.
        """
        client = Client()
        if not Config.TESTING:
            response = client.exchange_code_for_token(
                client_id=Config.CLIENT_ID,
                client_secret=Config.CLIENT_SECRET,
                code=code,
            )
            current_app.logger.debug("Response: " + str(response))
            client.access_token = response["access_token"]
            access_token = response["access_token"]
            refresh_token = response["refresh_token"]
            access_expr = datetime.fromtimestamp(response["expires_at"])
            athlete = client.get_athlete()
            user_id = athlete.id
            first_name = athlete.firstname
        else:
            access_token = "access"
            refresh_token = "refresh"
            access_expr = datetime.now() - timedelta(hours=5)
            user_id = 1
            first_name = "joe"

        # noinspection PyArgumentList
        u = User(
            id=user_id,
            first_name=first_name,
            access_token=access_token,
            refresh_token=refresh_token,
            access_expr=access_expr,
        )

        # Check if the user is already in the db
        if User.query.get(user_id) is None:
            db.session.add(u)
            db.session.commit()
            current_app.logger.info(f"New user added: {user_id}")
        else:
            u.refresh()
            current_app.logger.info(
                f"User {user_id} already found; updating token, logging in,"
                " and redirecting to dashboard"
            )
        return u

    def refresh(self):
        if self.expired:
            current_app.logger.info(
                f"User {self.id} access token expired at {self.access_expr}. "
                "Refreshing token."
            )
            r = Client().refresh_access_token(
                Config.CLIENT_ID, Config.CLIENT_SECRET, self.refresh_token
            )
            self.access_token = r["access_token"]
            self.refresh_token = r["refresh_token"]
            self.access_expr = datetime.fromtimestamp(r["expires_at"])
            db.session.commit()
        else:
            current_app.logger.info(
                f"User {self.id} doesn't expire until {self.access_expr}. "
                "Using existing token."
            )

    @property
    def expired(self) -> bool:
        return self.access_expr < datetime.now()

    # def refresh_user(self, )

    # @staticmethod
    # def subscribe():
    #     payload = {'client_id': Config.CLIENT_ID,
    #                'client_secret': Config.CLIENT_SECRET,
    #                'callback_url': 'http://' + Config.SERVER_NAME,
    #                'verify_token': Config.WEBHOOK_TOKEN}
    #     requests.post('https://api.strava.com/api/v3/push_subscriptions', data=payload)
    #     # Client.create_subscription(self.id, client_id=Config.CLIENT_ID, client_secret=Config.CLIENT_SECRET,
    #     #                            callback_url='http://ec2-13-58-76-233.us-east-2.compute.amazonaws.com:5000/handler', verify_token=Config.WEBHOOK_TOKEN)

    def make_rule(
        self,
        address: str,
        latitude: float,
        longitude: float,
        day_and_time: datetime,
        activity_name: str,
    ):
        """
        Makes a rule object from the associated data. Note that this method does not
        record the rule to the database. This is done a) so that the check_rule()
        method can be called on it before committing it to the database, and b) for
        unit testing.
        """
        new_rule = Rule(
            lat=latitude,
            lng=longitude,
            address=address,
            time=day_and_time,
            user_id=self.id,
            activity_name=activity_name,
        )
        return new_rule

    def check_rules_for_duplicate(self, rule_to_check: "Rule") -> bool:
        """
        Checks a given rule for duplicates among this user's already-existing rules.
        """
        for rule in self.rules:
            if rule.check_rule(rule=rule_to_check):
                return True
        return False

    def resolve_webhook(self, object_id: int):
        """
        Resolves a webhook event from Strava by retrieving the activity data and
        checking it against the user's existing rules. If a match is found, sends the
        request to Strava to rename it.
        """
        self.refresh()
        client = Client(access_token=self.access_token)
        activity = client.get_activity(object_id)
        # The Strava API doesn't give enough precision in its start latitude and
        # longitude values, so we have to call the raw stream of points to get what we
        # need.
        points = client.get_activity_streams(
            activity.id, types=["latlng"], resolution="low"
        )
        activity_start = points["latlng"].data[0]
        current_app.logger.info(
            f"Webhook event received: Activity {object_id}, User {self.id}, Starting"
            f"point {activity_start}, Starting time {activity.start_date_local}"
        )
        for rule in self.rules.all():
            current_app.logger.info(f"Checking {rule} against activity {object_id}")
            if rule.check_rule(activity_start, activity.start_date_local):
                # if not current_app.config.TESTING:
                client.update_activity(object_id, name=rule.activity_name)
                current_app.logger.info(
                    f"Activity {activity.id} renamed to {rule.activity_name} for {self}"
                )
                break  # No need to check any more activities
                # return rule.activity_name

    # # Collects the starting points of Strava activities for the user. Currently very slow.
    # def collect_start_points(self, number_of_markers=50):
    #     client = Client(self.access_token)
    #     activities = client.get_activities(limit=number_of_markers)
    #     streams = {activity.id: client.get_activity_streams(activity.id, types=['latlng'], resolution='low')
    #                for activity in activities}
    #     return {activity.id: streams[activity.id]['latlng'].data[0] for activity in activities}

    def __repr__(self):
        return f"<User {self.id}; First Name: {self.first_name}>"


class Rule(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Arbitrary id int
    lat = db.Column(db.Float)
    lng = db.Column(
        db.Float
    )  # The latitude and longitude associated to the rule are computed on creation
    address = db.Column(db.String)  # The address is stored for display back to the user
    time = db.Column(
        db.DateTime
    )  # The and day of the week associated to the rule. The datetime object is recorded as
    # a particular arbitrary day, but only the day of the week is used.
    append_date = db.Column(db.Boolean)
    activity_name = db.Column(db.String)  # The name for activities renamed by this rule
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))  # The associated user

    # Checks if a given timestamp (in units of seconds from Epoch) is within 1,000
    # seconds of the time specified in the rule, modulo 1 week

    def record(self):
        """
        Records the rule object to the database.
        """
        db.session.add(self)
        db.session.commit()
        current_app.logger.info(f"New rule added: {self}")

    def check_time(
        self, start_time=None, delta=timedelta(seconds=1000), rule=None
    ) -> bool:
        """
        Checks to see if the rule matches a given time and day of the week. Used for
        checking against new activities received from webhooks. Also used to validate
        new rules against duplicates, hence the optional rule argument.
        """
        if rule is None:
            difference = start_time - self.time
        else:
            difference = rule.time - self.time
        week: timedelta = timedelta(days=7)
        return ((difference % week) < delta) or ((-difference % week) < delta)

    def check_distance(self, start_point=None, radius: float = 0.25, rule=None) -> bool:
        """
        Checks to see if the rule matches a given location. Like the check_time()
        method, also used for duplicate-checking.
        """
        if rule is None:
            point_to_check = start_point
        else:
            point_to_check = (rule.lat, rule.lng)
        return distance((self.lat, self.lng), point_to_check).miles < radius

    def check_rule(
        self,
        start_point=None,
        start_time=None,
        delta=timedelta(seconds=1000),
        radius: float = 0.25,
        rule=None,
    ) -> bool:
        """
        The time and distance checks are being kept separate mostly for unit tests, 
        but most of the time, they're used
        together. So here's a function that combines them.
        """
        if rule is None:
            return self.check_time(start_time, delta) and self.check_distance(
                start_point, radius
            )
        else:
            return self.check_time(rule=rule) and self.check_distance(rule=rule)

    def delete_rule(self):
        """
        Deletes the rule from the database.
        """
        db.session.delete(self)
        db.session.commit()
        current_app.logger.info("{} deleted".format(self))

    def __repr__(self):
        return (
            f"<Location {self.address}: , Title: {self.activity_name}, User: {self.id}>"
        )


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

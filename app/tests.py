from datetime import datetime, timedelta
import unittest
from app import create_app, db
from app.models import User, Rule
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


class RuleModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_make_rule(self):
        u = User(id=1, first_name='joe')
        db.session.add(u)
        u.make_rule(address='14636 Martha St., Sherman Oaks, CA',
                    day_and_time=datetime(2018, 4, 19, 5, 30),
                    activity_name='test')
        rule = u.rules.one()
        self.assertEqual(rule.activity_name, 'test')
        self.assertAlmostEqual((rule.lat, rule.lng), (34.1730583, -118.4247143), 5)

    def test_check_distance(self):
        u = User(id=1, first_name='joe')
        db.session.add(u)
        u.make_rule(address='7100 East Green Lake Drive North, Seattle, WA',
                    day_and_time=datetime(2018, 4, 19, 5, 30),
                    activity_name='test')
        rule = u.rules.one()
        self.assertTrue(rule.check_distance((47.67986, -122.32724)))

    def test_check_time(self):
        u = User(id=1, first_name='joe')
        db.session.add(u)
        u.make_rule(address='7100 East Green Lake Drive North, Seattle, WA',
                    day_and_time=datetime(2018, 4, 19, 5, 30),
                    activity_name='test')
        rule = u.rules.one()
        self.assertTrue(rule.check_time(datetime(2018, 4, 26, 5, 20)))

    # def test_check_resolver(self):
    #     u = User(id=1,first_name='joe')
    #     db.session.add(u)
    #     u.make_rule(address='7100 East Green Lake Drive North, Seattle, WA',
    #                 day_and_time=datetime(2018,4,19,5,30),
    #                 activity_name='test')
    #     rule = u.rules.one()

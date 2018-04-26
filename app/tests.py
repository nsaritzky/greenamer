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
        u = User(id=1, first_name='joe')
        db.session.add(u)
        (u.make_rule(address='7100 East Green Lake Drive North, Seattle, WA',
                     day_and_time=datetime(2018, 4, 19, 5, 30),
                     activity_name='WUW')).record()
        (u.make_rule(address='Blue Moon Burgers Fremont, Seattle, WA',
                     day_and_time=datetime(2018, 4, 27, 6, 00),
                     activity_name='FLUR')).record()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # def test_make_rule(self):
    #     u = User.query.get(1)
    #     rule = u.rules.get()
    #     self.assertEqual(rule.activity_name, 'WUW')
    #     self.assertAlmostEqual((rule.lat, rule.lng), (34.1730583, -118.4247143), 5)

    def test_check_distance(self):
        u = User.query.get(1)
        rule = u.rules.filter_by(activity_name='WUW').one()
        self.assertTrue(rule.check_distance((47.67986, -122.32724)))
        self.assertFalse(rule.check_distance((47.6205131, -122.349303598832)))

    def test_check_time(self):
        u = User.query.get(1)
        rule = u.rules.filter_by(activity_name='WUW').one()
        self.assertTrue(rule.check_time(datetime(2018, 4, 26, 5, 20)))

    def test_check_rules_for_duplicate(self):
        u = User.query.get(1)
        # This one should match the FLUR rule above
        r_test1 = Rule(id=2, lat=47.6492247, lng=-122.34912, time=datetime(2018, 4, 20, 5, 55), user_id=1)
        # This one should not match because the location does not match either rule
        r_test2 = Rule(id=3, lat=47.6492247, lng=-112.32724, time=datetime(2018, 4, 20, 5, 55), user_id=1)
        # This one should not match because the time doesn't match either rule
        r_test3 = Rule(id=4, lat=47.6492247, lng=-122.34912, time=datetime(2018, 4, 20, 7, 55), user_id=1)
        self.assertTrue(u.check_rules_for_duplicate(r_test1))
        self.assertFalse(u.check_rules_for_duplicate(r_test2))
        self.assertFalse(u.check_rules_for_duplicate(r_test3))

    # def test_resolve_webhook(self):
    #     # noinspection PyArgumentList
    #     u = User(id=1, first_name='joe')
    #     db.session.add(u)
    #     u.make_rule(address='7100 East Green Lake Drive North, Seattle, WA',
    #                 day_and_time=datetime(2018, 4, 19, 5, 30),
    #                 activity_name='test1')
    #     u.make_rule(address='Blue Moon Burgers, Seattle WA',
    #                 day_and_time=datetime(2018, 4, 20, 6, 00),
    #                 activity_name='FLUR')
    #
    # @staticmethod
    # def set_up_test_user():
    #     u = User(id=1, first_name='joe')
    #     db.session.add(u)
    #     u.make_rule(address='7100 East Green Lake Drive North, Seattle, WA',
    #                 day_and_time=datetime(2018, 4, 19, 5, 30),
    #                 activity_name='WUW')
    #     u.make_rule(address='Blue Moon Burgers Fremont, Seattle, WA',
    #                 day_and_time=datetime(2018, 4, 27, 6, 00),
    #                 activity_name='FLUR')
    #     return u


    # def test_check_resolver(self):
    #     u = User(id=1,first_name='joe')
    #     db.session.add(u)
    #     u.make_rule(address='7100 East Green Lake Drive North, Seattle, WA',
    #                 day_and_time=datetime(2018,4,19,5,30),
    #                 activity_name='test')
    #     rule = u.rules.one()

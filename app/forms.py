from flask_wtf import FlaskForm
from wtforms import StringField, \
    SubmitField, SelectField, IntegerField, FloatField
from wtforms.widgets import HiddenInput
from wtforms.validators import DataRequired, ValidationError
from wtforms_components import TimeField
from geopy.geocoders import Nominatim
from flask import current_app
from flask_login import current_user
from app.models import Rule
from flask_login import current_user
from datetime import datetime, date, timedelta

TIME_DELTA = timedelta(seconds=1000)  # How far away a Strava event can be from a defining rule to get renamed
DISTANCE_DELTA = .25
ARBITRARY_MONDAY = date(2018, 4, 16)


# class LoginForm(FlaskForm):
#     username = StringField('Username', validators=[DataRequired()])
#     submit = SubmitField('Sign In')


# class TimeForm(FlaskForm):
#     hour = IntegerField('Hour')
#     minute = IntegerField('Minute')
#     am_pm = SelectField(choices=[('am', 'AM'), ('pm', 'PM')])

class DeleteForm(FlaskForm):
    submit = SubmitField('Delete')
    id = IntegerField('id', widget=HiddenInput(), validators=[DataRequired()])


class RuleForm(FlaskForm):
    location = StringField('Location', validators=[DataRequired()], render_kw={'placeholder': 'Location'})
    latitude = FloatField('latitude', widget=HiddenInput(), validators=[DataRequired()])
    longitude = FloatField('longitude', widget=HiddenInput(), validators=[DataRequired()])
    daysOfTheWeek = [(0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'),
                     (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')]
    days = SelectField('Days', choices=daysOfTheWeek, coerce=int, validators=[DataRequired()])
    time = TimeField('Time', validators=[DataRequired()])
    # appendDate = BooleanField('Add Date')
    activity_name = StringField('Activity Name', validators=[DataRequired()],
                                render_kw={'placeholder': 'Activity name'})
    submit = SubmitField('New Rule')

    def validate_location(self, field):
        current_app.logger.debug(field.data, self.days.data, self.time.data)
        rule_day = timedelta(days=self.days.data)
        rule_time = self.time.data
        provisional_rule = current_user.make_rule(address=self.location.data,
                                                  latitude=self.latitude,
                                                  longitude=self.longitude,
                                                  day_and_time=datetime.combine((ARBITRARY_MONDAY + rule_day), rule_time),
                                                  activity_name='')
        if current_user.check_rules_for_duplicate(provisional_rule):
            raise ValidationError('This overlaps with an already-existing rule')

    # def validate_time(self, field):
    #     if self.location.data is '' or self.days.data is None or field.data is None:
    #         raise ValidationError('Something was left blank')
    #     else:
    #         current_app.logger.debug(self.location.data, self.days.data, field.data)
    #         rule_day = timedelta(days=self.days.data)
    #         rule_time = field.data
    #         provisional_rule = current_user.make_rule(address=self.location.data,
    #                                                   day_and_time=datetime.combine((ARBITRARY_MONDAY + rule_day), rule_time),
    #                                                   activity_name='')
    #         if current_user.check_rules_for_duplicate(provisional_rule):
    #             raise ValidationError('This overlaps with an already-existing rule')


from flask_wtf import FlaskForm
from wtforms import StringField, FormField, \
    SubmitField, SelectField, BooleanField, IntegerField, DateField
from wtforms.validators import DataRequired, ValidationError
from wtforms_components import TimeField
from geopy.geocoders import Nominatim


# class LoginForm(FlaskForm):
#     username = StringField('Username', validators=[DataRequired()])
#     submit = SubmitField('Sign In')


# class TimeForm(FlaskForm):
#     hour = IntegerField('Hour')
#     minute = IntegerField('Minute')
#     am_pm = SelectField(choices=[('am', 'AM'), ('pm', 'PM')])


class RuleForm(FlaskForm):
    location = StringField('Location', render_kw={'placeholder': 'Address'})
    daysOfTheWeek = [(0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'),
                     (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')]
    days = SelectField('Days', choices=daysOfTheWeek, coerce=int, validators=[DataRequired()])
    time = TimeField('Time', validators=[DataRequired()])
    # appendDate = BooleanField('Add Date')
    activity_name = StringField('Activity Name', validators=[DataRequired()],
                                render_kw={'placeholder': 'Activity name'})
    submit = SubmitField('New Rule')

    def validate_location(self, location):
        geolocator = Nominatim(timeout=None)
        print(location.data)
        if geolocator.geocode(location.data) is None:
            raise ValidationError('Could not resolve address; please check it and try again.')

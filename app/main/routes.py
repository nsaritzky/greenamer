from datetime import datetime, date, timedelta

from flask import render_template, redirect, request, current_app
from flask_login import current_user, login_user, logout_user
from flask_login import login_required
from stravalib import Client

from app import db
from app.forms import RuleForm
from app.models import User
from config import Config

from flask_cdn import url_for
from app.main import bp

# I'm'a make a commit

TIME_DELTA = timedelta(seconds=1000)  # How far away a Strava event can be from a defining rule to get renamed
DISTANCE_DELTA = .25
ARBITRARY_MONDAY = date(2018, 4, 16)


@bp.route('/')
@bp.route('/index')
def index():
    if current_user.is_authenticated:
        current_app.logger.debug('User {} is already logged in, redirecting to dashboard'.format(current_user.id))
        return redirect(url_for('main.rules'))
    return render_template('index.html', title='Home', redirect=Config.OAUTH_URL, static=Config.STATIC_URL)


@bp.route('/auth')
def auth():
    access_denied = (request.args.get('error') == 'access_denied')

    if access_denied:
        return redirect('/index')

    code = request.args.get('code')
    user = User.add_user(code)
    login_user(user, remember=True)
    return redirect('/rules')


@bp.route('/rules', methods=['GET', 'POST'])
@login_required
def rules():
    form = RuleForm()

    # current_app.logger.warning(form.errors)
    if form.validate_on_submit():
        rule_day = timedelta(days=form.days.data)
        rule_time = form.time.data
        current_user.make_rule(form.location.data,
                               datetime.combine((ARBITRARY_MONDAY + rule_day), rule_time),
                               form.activity_name.data)
        current_app.logger.debug('Rule form validated')
        return redirect('/index')

    return render_template('rules.html', title='Rules', form=form)


# @bp.route('/delete')
# @login_required
# def delete():



@bp.route('/logout')
def logout():
    current_app.logger.debug('Logging out user {}'.format(current_user.id))
    logout_user()
    return redirect(url_for('main.index'))
from datetime import datetime, date, timedelta

from flask import render_template, redirect, url_for, request
from flask_login import current_user, login_user
from flask_login import login_required
from stravalib import Client

from app import db
from app.forms import RuleForm
from app.models import User
from config import Config

from app.main import bp

# I'm'a make a commit

import logging

TIME_DELTA = timedelta(seconds=1000)  # How far away a Strava event can be from a defining rule to get renamed
DISTANCE_DELTA = .25
ARBITRARY_MONDAY = date(2018, 4, 16)


@bp.route('/')
@bp.route('/index')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.rules'))
    return render_template('index.html', title='Home', redirect=Config.OAUTH_URL, static=Config.STATIC_URL)


@bp.route('/auth')
def auth():
    access_denied = (request.args.get('error') == 'access_denied')

    if access_denied:
        return redirect('/index')

    code = request.args.get('code')

    client = Client()
    if not Config.TESTING:
        token = client.exchange_code_for_token(client_id=Config.CLIENT_ID,
                                               client_secret=Config.CLIENT_SECRET,
                                               code=code)
        client = Client(access_token=token)
        athlete = client.get_athlete()
        user_id = athlete.id
        first_name = athlete.firstname
    else:
        token = 'token'
        user_id = 1
        first_name = 'joe'

    if User.query.get(user_id) is None:
        # noinspection PyArgumentList
        db.session.add(User(id=user_id, first_name=first_name, access_token=token))
        db.session.commit()
        logging.info('New user added: {}'.format(user_id))
    else:
        logging.info('User {} already found; logging in redirecting to dashboard'.format(user_id))
    login_user(User.query.get(user_id), remember=True)

    return redirect('/rules')


@bp.route('/rules', methods=['GET', 'POST'])
@login_required
def rules():
    form = RuleForm()

    logging.error(form.errors)
    if form.validate_on_submit():
        rule_day = timedelta(days=form.days.data)
        rule_time = form.time.data
        current_user.make_rule(form.location.data,
                               datetime.combine((ARBITRARY_MONDAY + rule_day), rule_time),
                               form.activity_name.data)
        logging.debug('Rule form validated')
        return redirect('/index')

    return render_template('rules.html', title='Rules', form=form)

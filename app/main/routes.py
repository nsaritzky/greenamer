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
    OAUTH_URL = Config.OAUTH_URL
    print(OAUTH_URL)

    return render_template('index.html', title='Home')


@bp.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    return render_template('login.html', title='Sign In')


@bp.route('/auth')
def auth():
    access_denied = (request.args.get('error') == 'access_denied')

    if access_denied:
        return redirect('/index')

    code = request.args.get('code')

    client = Client()
    token = client.exchange_code_for_token(client_id=Config.CLIENT_ID,
                                           client_secret=Config.CLIENT_SECRET,
                                           code=code)
    client = Client(access_token=token)
    athlete = client.get_athlete()

    if User.query.get(athlete.id) is None:
        print('User {} not found, trying to add to db'.format(athlete.id))
        # noinspection PyArgumentList
        db.session.add(User(id=athlete.id, first_name=athlete.firstname, access_token=token))
        db.session.commit()
        logging.info('New user added: {}'.format(athlete.id))
    login_user(User.query.get(athlete.id), remember=True)

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



import logging

from flask import request
from app.main import bp
from app.models import User
from config import Config

import requests


@bp.route('/handler', methods=['GET', 'POST'])
def webhook_handler():
    logging.debug(request.data)
    if request.method == 'GET':
        if request.args.get('hub.verify_token') == Config.WEBHOOK_TOKEN:
            payload = {'hub.challenge': request.args.get('hub.challenge')}
            requests.get('https://api.strava.com/api/v3/push_subscriptions', params=payload)
            return '', 200
    elif request.method == 'POST':
        logging.debug(request.data)
        data = request.get_json()
        if data['aspect_type'] == 'create':
            athlete: User = User.query.get(data['owner_id'])
            athlete.resolve_webhook(data['object_id'])
            logging.info('Strava webhook received: User {}, Activity {}'.format(athlete.id, data['object_d']))
            return '', 200
    return '', 200

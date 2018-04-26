import logging

from flask import request, current_app
from app.main import bp
from app.models import User
from config import Config
import json

import requests

# fasdfsad


@bp.route('/handler', methods=['GET', 'POST'])
def webhook_handler():
    current_app.logger.debug(request.data)
    if request.method == 'GET':
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        current_app.logger.info('Webhook subscription request got a response with verify token {}'.format(token))
        if token == Config.WEBHOOK_TOKEN:
            current_app.logger.info('Token accepted, sending challenge back')
            payload = json.dumps({'hub.challenge': challenge})
            return payload, 200
    elif request.method == 'POST':
        current_app.logger.debug(request.data)
        data = request.get_json()
        if data['aspect_type'] == 'create':
            athlete = User.query.get(int(data['owner_id']))
            if athlete is not None:
                athlete.resolve_webhook(data['object_id'])
                current_app.logger.info('Strava webhook received: User {}, Activity {}'.format(athlete.id, data['object_id']))
            else:
                current_app.logger.warning('You got a webhook for {}, but they weren\'t in the database'.format(data['owner_id']))
            return '', 200
    return '', 200

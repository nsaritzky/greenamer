import logging

from flask import request
from app.main import bp
from app.models import User
from config import Config


@bp.route('/handler', methods=['GET', 'POST'])
def webhook_handler():
    logging.debug(request.data)
    data = request.get_json()
    if 'hub.verify' in data:
        if data['hub.verify'] == Config.WEBHOOK_TOKEN:
            return '{"hub.challenge":"' + data['hub.challenge'] + '"}', 200
    if data['aspect_type'] == 'create':
        athlete: User = User.query.get(data['owner_id'])
        athlete.resolve_webhook(data['object_id'])

        return 'hi', 200
import logging

from flask import request, current_app
from app.main import bp
from app.models import User
from config import Config
import json

import requests


@bp.route("/handler", methods=["GET", "POST"])
def webhook_handler():
    current_app.logger.debug(request.get_data())
    if request.method == "GET":
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        current_app.logger.info(
            f"Webhook subscription request got a response with verify token {token}"
        )
        if token == Config.WEBHOOK_TOKEN:
            current_app.logger.info("Token accepted, sending challenge back")
            payload = json.dumps({"hub.challenge": challenge})
            return payload, 200
    elif request.method == "POST":
        current_app.logger.debug(request.get_data())
        data = request.get_json(force=True)
        if data["aspect_type"] == "create":
            athlete = User.query.get(int(data["owner_id"]))
            if athlete is not None:
                athlete.resolve_webhook(data["object_id"])
                current_app.logger.info(
                    f"Strava webhook received: User {athlete.id}, Activity {data['object_id']}"
                )
            else:
                current_app.logger.warning(
                    f"You got a webhook for {data['owner_id']}, but they weren't in the database"
                )
            return "", 200
    return "", 200

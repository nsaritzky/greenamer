from flask import Blueprint

bp = Blueprint('strava', __name__)

from app.webhooks import handler
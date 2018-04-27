from app.maps import bp
from flask import Flask, render_template
from flask_googlemaps import GoogleMaps, Map
from flask_login import login_required, current_user
from app.models import User, Rule
from config import Config
from stravalib import Client

NUMBER_OF_MARKERS: int = 10


@bp.route('/map')
@login_required
def map_page():
    start_points = current_user.collect_start_points(NUMBER_OF_MARKERS)
    myMap = Map(
        identifier="view-side",
        lat=37.4419,
        lng=-122.1419,
        markers=[(37.4419, -122.1419)]
    )

    return render_template('map.html', mymap=myMap)

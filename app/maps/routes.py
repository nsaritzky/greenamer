from app.maps import bp
from flask import Flask, render_template
from flask_googlemaps import GoogleMaps, Map
from flask_login import login_required, current_user
from app.models import User, Rule
from config import Config
from stravalib import Client

NUMBER_OF_MARKERS: int = 50


@bp.route('/map')
@login_required
def map_page():
    start_points = current_user.collect_start_points(NUMBER_OF_MARKERS)
    # logging.in
    myMap = Map(
        style="height:700px;width:600px",
        identifier="view-side",
        lat=list(start_points.values())[0][0],
        lng=list(start_points.values())[0][1],
        markers=list(start_points.values())
    )

    return render_template('map.html', mymap=myMap)

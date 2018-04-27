from app.maps import bp
from flask import Flask, render_template
from flask_googlemaps import GoogleMaps, Map
from flask_login import login_required
from config import Config
from stravalib import Client

@bp.route('/map')
@login_required
def map():
    myMap = Map(
        identifier="view-side",
        lat=37.4419,
        lng=-122.1419,
        markers=[(37.4419, -122.1419)]
    )

    return render_template('map.html', mymap=myMap)

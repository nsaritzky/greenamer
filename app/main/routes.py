from datetime import datetime, date, timedelta

from flask import render_template, redirect, request, current_app, flash, url_for
from flask_login import current_user, login_user, logout_user
from flask_login import login_required
from stravalib import Client

from app import db
from app.forms import RuleForm, DeleteForm
from app.models import User, Rule
from config import Config

# from flask_cdn import url_for
from app.main import bp

from motionless import DecoratedMap, LatLonMarker

# I'm'a make a commit

TIME_DELTA = timedelta(
    seconds=1000
)  # How far away a Strava event can be from a defining rule to get renamed
DISTANCE_DELTA = 0.25
ARBITRARY_MONDAY = date(2018, 4, 16)


def flash_errors(form):
    for field, errors in form.errors.items():
        field_name = getattr(form, field).label.text
        if field_name is "latitude":
            flash("Could not resolve location; please check the address and try again.")
        elif field_name is not "longitude":
            for error in errors:
                flash(
                    "Error in the %s field - %s"
                    % (getattr(form, field).label.text, error)
                )


@bp.route("/")
@bp.route("/index")
def index():
    if current_user.is_authenticated and current_user.refresh_token is not None:
        current_app.logger.info(
            f"User {current_user.id} is already logged in, redirecting to dashboard"
        )
        return redirect(url_for("main.rules"))
    return render_template(
        "index.html", title="Home", redirect=Config.OAUTH_URL, static=Config.STATIC_URL
    )


@bp.route("/auth")
def auth():
    access_denied = request.args.get("error") == "access_denied"

    if access_denied:
        return redirect("/index")

    code = request.args.get("code")
    user = User.add_user(code)
    login_user(user, remember=True)
    return redirect("/rules")


@bp.route("/rules", methods=["GET", "POST"])
@login_required
def rules():
    form = RuleForm()
    delete_forms = {rule.id: DeleteForm(obj=rule) for rule in current_user.rules}

    map_images = {}
    for rule in current_user.rules:
        dmap = DecoratedMap(key=Config.GOOGLEMAPS_KEY, size_x=280, size_y=280)
        dmap.add_marker(LatLonMarker(rule.lat, rule.lng))
        map_images[rule.id] = dmap.generate_url()

    # This is a hack to get the delete buttons to ignore submission of new rule forms.
    # It is inelegant.
    if form.errors is not {}:
        current_app.logger.info(form.errors)
    if form.validate_on_submit():
        for rule in current_user.rules:
            delete_forms[rule.id].id.data = None
        rule_day = timedelta(days=form.days.data)
        rule_time = form.time.data
        new_rule = current_user.make_rule(
            form.location.data,
            form.latitude.data,
            form.longitude.data,
            datetime.combine((ARBITRARY_MONDAY + rule_day), rule_time),
            form.activity_name.data,
        )
        new_rule.record()
        current_app.logger.debug("Rule form validated")
        return redirect("/index")

    if DeleteForm().validate_on_submit():
        rule = Rule.query.get(DeleteForm().id.data)
        rule.delete_rule()
        return redirect(url_for("main.rules"))

    flash_errors(form)

    return render_template(
        "rules.html",
        title="Rules",
        form=form,
        delete_forms=delete_forms,
        map_urls=map_images,
        maps_key=Config.GOOGLEMAPS_KEY,
    )


@bp.route("/about")
def about():
    return render_template("about.html")


@bp.route("/logout")
def logout():
    current_app.logger.debug("Logging out user {}".format(current_user.id))
    logout_user()
    return redirect(url_for("main.index"))

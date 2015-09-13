from flask import current_app
from travelbudget.database import db_session
from travelbudget.models import Trip
from travelbudget.utilities import summary
import flask
import datetime

USER_ID = 1
main_bp = flask.Blueprint('main',
                          __name__)

@main_bp.route('/')
def home():
    today = datetime.date.today()
    trips = Trip.query.filter_by(user_id=USER_ID).\
        filter(Trip.end_date >= today).\
        order_by(Trip.start_date)

    future_trips = []
    current_trips = []
    for trip in trips:
        if trip.start_date <= today:
            current_trips.append(trip)
        else:
            future_trips.append(trip)
    return flask.render_template('main/index.html',
                                 current_trips=current_trips,
                                 future_trips=future_trips)
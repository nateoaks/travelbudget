from flask import current_app
from travelbudget.database import db_session
from travelbudget.models import Currency, Trip
from travelbudget.utilities import summary
import flask

USER_ID = 1
trips_bp = flask.Blueprint('trips',
                           __name__,
                           url_prefix='/trips')

@trips_bp.route('/<int:trip_id>/')
def view(trip_id):
    trip = Trip.query.get(trip_id)
    trip.cash = summary.cash_totals(trip_id)
    return flask.render_template('trips/view.html', trips=[trip])

@trips_bp.route('/')
def view_all():
    trips = Trip.query.all()
    for trip in trips:
        trip.cash = summary.cash_totals(trip.id)
    return flask.render_template('trips/view.html', trips=trips)

@trips_bp.route('/add/', methods=['GET','POST'])
def add():
    trip = None
    if flask.request.method == 'POST':
        current_app.logger.info(flask.request.form)
        trip = Trip(
            user_id=USER_ID,
            name=flask.request.form['name'],
            start_date=flask.request.form['start_date'],
            end_date=flask.request.form['end_date'],
            currency_id=flask.request.form['currency_id'],
        )

        db_session.add(trip)
        db_session.commit()

        result = flask.redirect(flask.url_for('trips.view', trip_id=trip.id, _external=True))
        current_app.logger.info(dir(result))
        current_app.logger.info(result)
        return result

    currencies = {c.id: c.iso_code for c in Currency.query.all()}

    return flask.render_template('trips/add.html',
                                 currencies=currencies,
                                 trip=trip)

@trips_bp.route('/summary/<int:trip_id>/')
def trip_summary(trip_id):
    category_expenses = summary.total_spent_by_category(trip_id, add_category_name=True)
    daily_budget_remaining = summary.current_daily_budget(trip_id)
    total_spent_trip = summary.total_spent_trip(trip_id)
    total_trip_budget = summary.total_trip_budget(trip_id)
    return flask.render_template('trips/summary.html',
                                 category_expenses=category_expenses,
                                 daily_budget_remaining=daily_budget_remaining,
                                 total_spent_trip=total_spent_trip,
                                 total_trip_budget=total_trip_budget)


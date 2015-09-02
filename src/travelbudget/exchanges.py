from flask import current_app
from travelbudget.database import db_session
from travelbudget.models import Account, Expense, MoneyExchange, Trip
from travelbudget.utilities import summary
import flask
import datetime

DAILY_CURRENCY_ID = 1
CASH_ACCOUNT_ID = 1
CASH_CATEGORY_ID = 4
USER_ID = 1
exchanges_bp = flask.Blueprint('exchanges',
                              __name__,
                              url_prefix='/exchanges')

@exchanges_bp.route('/<int:money_exchange_id>/')
def view(money_exchange_id):
    exchange = MoneyExchange.query.get(money_exchange_id)
    return flask.render_template('exchanges/view.html', exchanges=[exchange])

@exchanges_bp.route('/trip-<int:trip_id>/')
def view_all(trip_id):
    exchanges = MoneyExchange.query.filter_by(trip_id=trip_id).order_by(MoneyExchange.exchange_date)
    return flask.render_template('exchanges/view.html', exchanges=exchanges)

@exchanges_bp.route('/add/trip-<int:trip_id>/', methods=['GET','POST'])
def add(trip_id):
    trip = Trip.query.get(trip_id)

    exchange = None
    if flask.request.method == 'POST':
        current_app.logger.info(flask.request.form)

        preferred_currency_expense_amount = 0
        if int(flask.request.form['expense_currency_id']) == int(trip.preferred_currency_id):
            preferred_currency_expense_amount = flask.request.form['expense_amount']
        elif flask.request.form['expense_account_id'] == CASH_ACCOUNT_ID:
            results = summary.get_cash_expense_in_preferred_currency(trip_id,
                                                                     flask.request.form['expense_amount'],
                                                                     flask.request.form['expense_currency_id'])
            for res in results:
                preferred_currency_expense_amount += res['preferred_currency_amount']
                db_session.add(res['money_exchange'])

        try:
            exchange = MoneyExchange(
                trip_id=trip_id,
                exchange_date=flask.request.form['date'],
                income_currency_id=flask.request.form['income_currency_id'],
                income_account_id=flask.request.form['income_account_id'],
                income_amount=flask.request.form['income_amount'],
                expense_currency_id=flask.request.form['expense_currency_id'],
                expense_account_id=flask.request.form['expense_account_id'],
                expense_amount=flask.request.form['expense_amount'],
                expense_fee=flask.request.form['expense_fee'] or 0,
                preferred_currency_expense_amount=preferred_currency_expense_amount,
                created=datetime.datetime.now()
            )

            db_session.add(exchange)
            db_session.commit()
        except:
            current_app.logger.exception('failed')

        return flask.redirect(flask.url_for('exchanges.view', money_exchange_id=exchange.id))

    accounts = {a.id: a.name for a in Account.query.filter_by(user_id=USER_ID)}
    currencies = {c.id: c.iso_code for c in trip.currencies}
    today = datetime.date.today()

    return flask.render_template('exchanges/add.html',
                                 trip_id=trip_id,
                                 accounts=accounts,
                                 currencies=currencies,
                                 exchange=exchange,
                                 today=today)

from flask import current_app
from travelbudget.database import db_session
from travelbudget.models import Account, Category, DailyCurrency, Expense, Trip
from travelbudget.utilities import summary, json_
import flask
import datetime
import json

DAILY_CURRENCY_ID = 1
USER_ID = 1
expenses_bp = flask.Blueprint('expenses',
                              __name__,
                              url_prefix='/expenses')

@expenses_bp.route('/<int:expense_id>/')
def view(expense_id):
    expense = Expense.query.get(expense_id)
    return flask.render_template('expenses/view.html', expenses=[expense])

@expenses_bp.route('/trip-<int:trip_id>/')
def view_all(trip_id):
    # expenses = summary.get_expenses(trip_id=1, start_date='2015-04-10', end_date='2015-04-20', category_ids=[1,2,3])
    expenses = Expense.query.filter_by(trip_id=trip_id)
    return flask.render_template('expenses/view.html', expenses=expenses)

@expenses_bp.route('/add/trip-<int:trip_id>/', methods=['GET','POST'])
def add(trip_id):

    expense = None
    if flask.request.method == 'POST':
        current_app.logger.info(flask.request.form)

        trip = Trip.query.get(trip_id)
        daily_currency = DailyCurrency.query.filter_by(currency_id=flask.request.form['currency_id'],
                                                       current=1).first()
        current_app.logger.info('{}, {}, {}'.format(trip.preferred_currency.daily_currency.conversion_rate,
                                                    daily_currency.conversion_rate,
                                                    float(flask.request.form['amount'])))

        preferred_currency_amount = 0
        results = summary.get_cash_expense_in_preferred_currency(trip_id,
                                                                 flask.request.form['amount'],
                                                                 flask.request.form['currency_id'])

        expense_notes = []
        for res in results:
            preferred_currency_amount += res['preferred_currency_amount']
            note = {
                'amount': res['amount'],
                'preferred_currency_amount': res['preferred_currency_amount'],
                'money_exchange_id': None
            }
            if res['money_exchange']:
                db_session.add(res['money_exchange'])
                note['money_exchange_id'] = res['money_exchange'].id
            expense_notes.append(note)


        expense = Expense(
            trip_id=trip_id,
            expense_date=flask.request.form['date'],
            amount=flask.request.form['amount'],
            preferred_currency_amount=preferred_currency_amount,
            currency_id=flask.request.form['currency_id'],
            daily_currency_id=DAILY_CURRENCY_ID,
            account_id=flask.request.form['account_id'],
            category_id=flask.request.form['category_id'],
            country_id=flask.request.form['country_id'],
            description=flask.request.form['description'],
            notes=json.dumps(expense_notes, cls=json_.ExpenseEncoder),
            created=datetime.datetime.now()
        )

        db_session.add(expense)
        db_session.commit()

        return flask.redirect(flask.url_for('expenses.view', expense_id=expense.id))

    trip = Trip.query.get(trip_id)
    accounts = {a.id: a.name for a in Account.query.filter_by(user_id=USER_ID)}
    currencies = {c.id: c.iso_code for c in trip.currencies}
    countries = {c.id: c.country_name for c in trip.countries}
    categories = {c.id: c.category_name for c in Category.query.all()}
    today = datetime.date.today()

    return flask.render_template('expenses/add.html',
                                 trip_id=trip_id,
                                 accounts=accounts,
                                 categories=categories,
                                 countries=countries,
                                 currencies=currencies,
                                 expense=expense,
                                 today=today)

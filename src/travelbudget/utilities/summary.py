from travelbudget.models import Category, Currency, DailyCurrency, Expense, MoneyExchange, Trip
from travelbudget.database import db_session
from sqlalchemy import func
from decimal import Decimal
import collections
import datetime

CASH_ACCOUNT_ID = 1

def get_expenses(trip_id, category_ids=None, start_date=None, end_date=None):
    """
    Returns a list of expenses based on filter args
    """
    expense_filter = Expense.query.filter(Expense.trip_id==trip_id)
    if category_ids:
        expense_filter = expense_filter.filter(Expense.category_id.in_(category_ids))
    if start_date:
        expense_filter = expense_filter.filter(Expense.expense_date.between(start_date, end_date))

    return expense_filter

def cash_totals(trip_id):
    """
    Returns dict of cash totals by currency
    """
    incomes = db_session.query(MoneyExchange.income_currency_id,
                               func.sum(MoneyExchange.income_amount)).\
        filter_by(trip_id=trip_id).\
        group_by(MoneyExchange.income_currency_id)
    exchanges = db_session.query(MoneyExchange.expense_currency_id,
                                 func.sum(MoneyExchange.expense_amount)).\
        filter_by(trip_id=trip_id).\
        filter_by(expense_account_id=CASH_ACCOUNT_ID).\
        group_by(MoneyExchange.expense_currency_id)

    cash_by_currency = collections.defaultdict(Decimal)
    for i in incomes:
        cash_by_currency[i[0]] += i[1]
    for e in exchanges:
        cash_by_currency[e[0]] -= e[1]

    expenses = db_session.query(Expense.currency_id,
                                func.sum(Expense.amount)).\
        filter_by(trip_id=trip_id).\
        filter_by(account_id=CASH_ACCOUNT_ID).\
        filter(~Expense.category_id.in_([4,5])).\
        group_by(Expense.currency_id)

    for e in expenses:
        cash_by_currency[e[0]] -= e[1]

    return dict(cash_by_currency)

def get_cash_expense_in_preferred_currency(trip_id, amount, currency_id):
    """
    Returns list of results for cash based on what is left in reserves by currency
    """
    exchange = MoneyExchange.query.\
        filter_by(trip_id=trip_id,
                  income_account_id=CASH_ACCOUNT_ID,
                  income_currency_id=currency_id).\
        filter(MoneyExchange.amount_left > 0).\
        order_by(MoneyExchange.exchange_date)

    results = []
    cur_amount = Decimal(amount)

    for cur_exchange in exchange:
        amount_from_cur_exchange = min(cur_amount, cur_exchange.amount_left)
        cur_amount -= amount_from_cur_exchange
        preferred_currency_amount = amount_from_cur_exchange / cur_exchange.income_amount * cur_exchange.preferred_currency_expense_amount
        cur_exchange.amount_left = cur_exchange.amount_left - amount_from_cur_exchange
        results.append({'amount': amount_from_cur_exchange,
                        'money_exchange': cur_exchange,
                        'preferred_currency_amount': preferred_currency_amount})
        if amount_from_cur_exchange == 0:
            break

    return results

def total_spent_by(trip_id, group_by):
    """
    Return total spent for trip in dict indexed by {group_by}
    """
    expenses = db_session.query(Expense.category_id,
                                func.sum(Expense.preferred_currency_amount)).\
        filter_by(trip_id=trip_id).\
        group_by(getattr(Expense, group_by))
    return expenses

def total_spent_by_category(trip_id, add_category_name=False):
    category_expenses = total_spent_by(trip_id, 'category_id')
    expenses = {e[0]: {'category_id': e[0], 'amount': e[1]} for e in category_expenses}

    if add_category_name:
        categories = Category.query.filter(Category.id.in_(expenses.keys()))
        for c in categories:
            expenses[c.id]['category'] = c.category_name

    return expenses

def total_spent_by_country(trip_id):
    country_expenses = total_spent_by(trip_id, 'country_id')
    countries = {e[0]: e[1] for e in country_expenses}
    return countries


def total_spent(trip_id):
    return db_session.query(func.sum(Expense.amount)).\
        filter_by(trip_id=trip_id)[0][0]

def current_daily_budget(trip_id):
    trip = Trip.query.get(trip_id)
    total_trip_days = (trip.end_date - trip.start_date).days
    trip_budget = trip.trip_budget or trip.daily_budget * total_trip_days
    trip_days_passed = (min(trip.end_date, datetime.date.today()) - trip.start_date).days

    total_budget_left = trip_budget - total_spent(trip_id)
    return total_budget_left / (total_trip_days - trip_days_passed)





# def total_spent(trip_id, currency_id, category_ids=None, start_date=None, end_date=None):
#
#     # get all daily currencies for {currency_id}
#     daily_currencies = DailyCurrency.query.filter_by(currency_idid=currency_id)
#     daily_currency_date_map = {dc.date: dc.conversion_rate for dc in daily_currencies}
#
#     expense_sum = sum([e.amount / e.daily_currency.conversion_rate * daily_currency_date_map[e.date].conversion_rate for e in expenses])
#     return expense_sum
#
# def trip_expenses(trip_id, currency_id):
#     expenses = Expense.query.filter_by(trip_id=trip_id)
#
#     # get all daily currencies for {currency_id}
#     daily_currencies = DailyCurrency.query.filter_by(currency_id=currency_id)
#     daily_currency_date_map = {dc.date: dc.conversion_rate for dc in daily_currencies}
#
#     for e in expenses:
#         e.to_currency_amount = e.amount / e.daily_currency.conversion_rate * daily_currency_date_map[e.date].conversion_rate
#
#     return expenses
#
# def trip_exenses_by_date(trip_id, currency_id, start_date, end_date):
#     pass
#

from travelbudget.database import db_session
from travelbudget.models import Category, Country, Currency, DailyCurrency, Expense, Income
import csv
import datetime
import re
import time

COUNTRIES = {}
for c in Country.query.all():
    COUNTRIES[c.country_name] = c.id

CATEGORIES = {}
for c in Category.query.all():
    CATEGORIES[c.category_name] = c.id

CURRENCIES = {}
for c in Currency.query.all():
    CURRENCIES[c.iso_code] = c.id

DAILY_CURRENCIES = {}
for dc in DailyCurrency.query.filter_by(current=1):
    DAILY_CURRENCIES[dc.currency_id] = dc.id

cash = False
with open('/vagrant/south_america-2.csv') as f:
    d = csv.DictReader(f)

    for r in d:

        if r['country']:
            current_country = r['country']
            current_currency = r['currency']
            continue

        if r['date']:
            current_date = time.strftime('%Y-%m-%d', time.strptime(r['date'], '%m/%d/%Y'))

        if r['category'] in ('Cash',):
            cash = True
            exp_insert = {
                'trip_id': 1,
                'expense_date': current_date,
                'country_id': COUNTRIES[current_country],
                'account_id': 3,
                'category_id': 4,
                'created': datetime.datetime.now(),
            }

            if r['credit_usd']:
                exp_insert['amount'] = re.sub('[,$]','', r['credit_usd'])
                exp_insert['currency_id'] = CURRENCIES['USD']
                exp_insert['daily_currency_id'] = DAILY_CURRENCIES[CURRENCIES['USD']]
            elif r['cash_expense_usd']:
                exp_insert['amount'] = re.sub('[,$]','', r['cash_expense_usd'])
                exp_insert['currency_id'] = CURRENCIES['USD']
                exp_insert['daily_currency_id'] = DAILY_CURRENCIES[CURRENCIES['USD']]
            elif r['cash_expense_foreign']:
                exp_insert['amount'] = re.sub('[,$]','', r['cash_expense_foreign'])
                exp_insert['currency_id'] = CURRENCIES[current_currency]
                exp_insert['daily_currency_id'] = DAILY_CURRENCIES[CURRENCIES[current_currency]]

            print exp_insert
            expense = Expense(**exp_insert)
            db_session.add(expense)
            db_session.commit()
            print 'Expense: {}'.format(expense.id)

            inc_insert = {
                'trip_id': 1,
                'income_date': current_date,
                'account_id': 1,
                'expense_id': expense.id,
                'amount': re.sub('[,$]','', r['cash_income_foreign']),
                'currency_id': CURRENCIES[current_currency],
                'created': datetime.datetime.now(),
            }

            if r['cash_income_foreign']:
                inc_insert['amount'] = re.sub('[,$]','', r['cash_income_foreign'])
                inc_insert['currency_id'] = CURRENCIES[current_currency],
            elif r['cash_income_usd']:
                inc_insert['amount'] = re.sub('[,$]','', r['cash_income_usd'])
                inc_insert['currency_id'] = CURRENCIES['USD'],

            print inc_insert
            income = Income(**inc_insert)
            db_session.add(income)
            db_session.commit()

            print 'Income: {}'.format(income.id)
            continue

        if r['category'] in ('Cash Fee',):
            if not cash:
                raise Exception('Uh oh, last transaction was not a cash expense')

            exp_insert = {
                'trip_id': 1,
                'expense_date': current_date,
                'amount': re.sub('[,$]','', r['credit_usd']),
                'currency_id': CURRENCIES['USD'],
                'country_id': COUNTRIES[current_country],
                'daily_currency_id': DAILY_CURRENCIES[CURRENCIES['USD']],
                'account_id': 3,
                'category_id': 5,
                'parent_expense_id': expense.id,
                'created': datetime.datetime.now(),
            }
            print 'Cash Fee: {}'.format(exp_insert)

            expense = Expense(**exp_insert)
            db_session.add(expense)
            db_session.commit()

            print 'Cash Fee: {}'.format(expense.id)
            continue

        cash = False

        if r['category'] == '':
            # print 'Skipping due to no category: {}'.format(r)
            continue

        insert = {
            'trip_id': 1,
            'expense_date': current_date,
            'description': r['description'],
            'days_spread': r['nights'] if r['nights'] else None
        }

        insert['country_id'] = COUNTRIES[current_country]
        insert['category_id'] = CATEGORIES[r['category']]
        insert['created'] = datetime.datetime.now()

        if r['cash_expense_foreign']:
            insert['amount'] = r['cash_expense_foreign']
            insert['currency_id'] = CURRENCIES[current_currency]
            insert['daily_currency_id'] = DAILY_CURRENCIES[CURRENCIES[current_currency]]
            insert['account_id'] = 1

        elif r['cash_expense_usd']:
            insert['amount'] = r['cash_expense_usd']
            insert['currency_id'] = CURRENCIES['USD']
            insert['daily_currency_id'] = DAILY_CURRENCIES[CURRENCIES['USD']]
            insert['account_id'] = 1
        elif r['credit_usd']:
            insert['amount'] = r['credit_usd']
            insert['currency_id'] = CURRENCIES['USD']
            insert['daily_currency_id'] = DAILY_CURRENCIES[CURRENCIES['USD']]
            insert['account_id'] = 2

        insert['amount'] = re.sub('[,$]','', insert['amount'])
        print insert
        expense = Expense(**insert)
        db_session.add(expense)
        db_session.commit()
        print expense.id

        if r['cash_expense_foreign'] and r['credit_usd']:
            insert['amount'] = r['credit_usd']
            insert['currency_id'] = CURRENCIES['USD']
            insert['daily_currency_id'] = DAILY_CURRENCIES[CURRENCIES['USD']]
            insert['account_id'] = 2
            insert['parent_expense_id'] = expense.id

            # parent_expense = Expense.query.filter_by(expense_date=insert['expense_date'],
            #                                          description=insert['description'],
            #                                          currency_id=CURRENCIES[current_currency]).first()
            # if parent_expense:
            #     insert['parent_expense_id'] = parent_expense.id

            insert['amount'] = re.sub('[,$]','', insert['amount'])
            print insert
            expense = Expense(**insert)
            db_session.add(expense)
            db_session.commit()
            print expense.id


from flask import current_app
from travelbudget.database import db_session
from travelbudget.models import Expense
from travelbudget.utilities.summary import *
import flask
import datetime

test_bp = flask.Blueprint('test',
                          __name__,
                          url_prefix='/test')

@test_bp.route('/')
def index():
    # result = Expense.query.all()
    result = get_expenses(1,
                          [1,2,3],
                          # datetime.date(2015,01,01),
                          # datetime.date(2015,04,01)
                          )
    for e in result:
        print e


    return flask.render_template('test/index.html')


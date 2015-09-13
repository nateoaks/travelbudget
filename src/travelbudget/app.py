from flask import Flask, jsonify
from logging import Formatter, INFO
from logging.handlers import TimedRotatingFileHandler
from travelbudget.database import db_session, engine
from travelbudget.exchanges import exchanges_bp
from travelbudget.expenses import expenses_bp
from travelbudget.main import main_bp
from travelbudget.trips import trips_bp
from travelbudget.utilities.filters import filters_bp
from flask.ext.sqlalchemy import _EngineDebuggingSignalEvents
from flask_debugtoolbar import DebugToolbarExtension

# from travelbudget.test import test_bp

app = Flask(__name__)
app.config.from_object('travelbudget.config.BaseConfig')

# set up file logging
file_handler = TimedRotatingFileHandler('/var/log/tb.log', when='d')
file_handler.setFormatter(Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
app.logger.addHandler(file_handler)
app.logger.setLevel(INFO)
app.logger.info('test')

# for debug toolbar
app.debug = True
app.config['SECRET_KEY'] = 'xyz'
toolbar = DebugToolbarExtension(app)

# teardown DB connection
@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

app.register_blueprint(main_bp)
app.register_blueprint(trips_bp)
app.register_blueprint(exchanges_bp)
app.register_blueprint(expenses_bp)
app.register_blueprint(filters_bp)

# app.register_blueprint(test_bp)

_EngineDebuggingSignalEvents(engine, app.import_name).register()


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

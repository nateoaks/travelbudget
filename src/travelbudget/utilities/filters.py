import jinja2
import flask

filters_bp = flask.Blueprint('filters', __name__)

@jinja2.contextfilter
@filters_bp.app_template_filter()
def format_currency(context, amount, currency):
    if currency.position == 'before':
        return '{}{:,.2f}'.format(currency.symbol, amount)
    else:
        return '{}{:,.2f}'.format(amount, currency.symbol)


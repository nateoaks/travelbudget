from travelbudget.models import Currency

currencies = {c.id: c for c in Currency.query.all()}

def convert(amount, ex_from, ex_to):
    return amount * ex_to / ex_from
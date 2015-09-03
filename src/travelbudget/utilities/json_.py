import decimal
import json

class ExpenseEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return str(o)
        return super(ExpenseEncoder, self).default(o)

from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Table
from travelbudget.database import Base
import datetime

class Account(Base):
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    name = Column(String(255))
    created = Column(DateTime)

class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    category_name = Column(String(255))
    created = Column(DateTime)

class Country(Base):
    __tablename__ = 'countries'
    id = Column(Integer, primary_key=True)
    country_code = Column(String(2))
    country_name = Column(String(45))
    currency_code = Column(String(3))
    currency_id = Column(Integer)
    continent_name = Column(String(15))
    created = Column(DateTime)

class Currency(Base):
    __tablename__ = 'currencies'
    id = Column(Integer, primary_key=True)
    iso_code = Column(String(3))
    symbol = Column(String(3))
    unicode_symbol = Column(String(8))
    position = Column(String(6))
    comments = Column(String(255))
    created = Column(DateTime)

    daily_currency = relationship("DailyCurrency",
                                  primaryjoin="and_(Currency.id==DailyCurrency.currency_id, DailyCurrency.current==1)",
                                  uselist=False)

class DailyCurrency(Base):
    __tablename__ = 'daily_currencies'
    id = Column(Integer, primary_key=True)
    currency_id = Column(Integer, ForeignKey('currencies.id'))
    date = Column(DateTime)
    conversion_rate = Column(Float)
    current = Column(Integer)
    created = Column(DateTime)

class Expense(Base):
    __tablename__ = 'expenses'
    id = Column(Integer, primary_key=True)
    trip_id = Column(Integer, ForeignKey('trips.id'))
    expense_date = Column(DateTime)
    amount = Column(Float)
    preferred_currency_amount = Column(Float)
    currency_id = Column(Integer, ForeignKey('currencies.id'))
    daily_currency_id = Column(Integer, ForeignKey('daily_currencies.id'))
    country_id = Column(Integer, ForeignKey('countries.id'))
    account_id = Column(Integer, ForeignKey('accounts.id'))
    category_id = Column(Integer, ForeignKey('categories.id'))
    parent_expense_id = Column(Integer)
    description = Column(String(255))
    days_spread = Column(Integer)
    created = Column(DateTime)

    trip = relationship('Trip', backref='expenses')
    currency = relationship('Currency')
    category = relationship('Category')
    daily_currency = relationship('DailyCurrency')

    def __init__(self, trip_id=None, expense_date=None, amount=None, preferred_currency_amount=None,
                 currency_id=None, daily_currency_id=None, country_id=None, account_id=None,
                 category_id=None, description=None, days_spread=None, parent_expense_id=None,
                 created=None):
        self.trip_id = trip_id
        self.expense_date = expense_date
        self.amount = amount
        self.preferred_currency_amount = preferred_currency_amount
        self.currency_id = currency_id
        self.daily_currency_id = daily_currency_id
        self.country_id = country_id
        self.account_id = account_id
        self.category_id = category_id
        self.description = description
        self.days_spread = days_spread
        self.parent_expense_id = parent_expense_id
        self.created = created

    def __repr__(self):
        return '<Id: {id}, Description: {description}>'.format(**self.__dict__)

class MoneyExchange(Base):
    __tablename__ = 'money_exchanges'
    id = Column(Integer, primary_key=True)
    trip_id = Column(Integer, ForeignKey('trips.id'))
    exchange_date = Column(DateTime)
    amount_left = Column(Float)
    income_currency_id = Column(Integer, ForeignKey('currencies.id'))
    income_account_id = Column(Integer, ForeignKey('accounts.id'))
    income_amount = Column(Float)
    expense_currency_id = Column(Integer, ForeignKey('currencies.id'))
    expense_account_id = Column(Integer, ForeignKey('accounts.id'))
    expense_amount = Column(Float)
    preferred_currency_expense_amount = Column(Float)
    expense_fee = Column(Float)
    created = Column(DateTime)

    trip = relationship('Trip', backref='money_exchanges')
    income_currency = relationship('Currency', foreign_keys=[income_currency_id])
    income_account = relationship('Account', foreign_keys=[income_account_id])
    expense_currency = relationship('Currency', foreign_keys=[expense_currency_id])
    expense_account = relationship('Account', foreign_keys=[expense_account_id])

    def __init__(self, trip_id=None, exchange_date=None,
                 income_amount=None, income_currency_id=None, income_account_id=None,
                 expense_amount=None, expense_currency_id=None, expense_account_id=None,
                 expense_fee=None, preferred_currency_expense_amount=None,
                 created=None):
        self.trip_id = trip_id
        self.exchange_date = exchange_date
        self.amount_left = income_amount
        self.income_amount = income_amount
        self.income_currency_id = income_currency_id
        self.income_account_id = income_account_id
        self.expense_amount = expense_amount
        self.expense_currency_id = expense_currency_id
        self.expense_account_id = expense_account_id
        self.preferred_currency_expense_amount = preferred_currency_expense_amount
        self.expense_fee = expense_fee
        self.created = created

    def __repr__(self):
        return '<Id: {id}, Exchange Date: {exchange_date}>'.format(**self.__dict__)

class Tag(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    created = Column(DateTime)

trip_to_country = Table(
    'trips_to_countries',
    Base.metadata,
    Column('trip_id', Integer, ForeignKey('trips.id')),
    Column('country_id', Integer, ForeignKey('countries.id'))
)

trip_to_currency = Table(
    'trips_to_currencies',
    Base.metadata,
    Column('trip_id', Integer, ForeignKey('trips.id')),
    Column('currency_id', Integer, ForeignKey('currencies.id'))
)

class Trip(Base):
    __tablename__ = 'trips'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    name = Column(String(255))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    preferred_currency_id = Column(Integer, ForeignKey('currencies.id'))
    daily_budget = Column(Float)
    trip_budget = Column(Float)
    created = Column(DateTime)

    countries = relationship('Country', secondary=trip_to_country)
    preferred_currency = relationship('Currency')
    currencies = relationship('Currency', secondary=trip_to_currency)

    def __init__(self, user_id, name, start_date, end_date, currency_id):
        self.user_id = user_id
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.created = datetime.datetime.now()
        self.preferred_currency_id = currency_id

    def __repr__(self):
        return '<Id: {id}, Name: {name}>'.format(**self.__dict__)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)

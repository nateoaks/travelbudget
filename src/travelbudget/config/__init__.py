MYSQL_CONFIG = dict(
    MYSQL_HOST='db',
    MYSQL_USER='tb',
    MYSQL_PASSWORD='tbpass',
    MYSQL_DB='travelbudget'
)
MYSQL_DATABASE_URI = "mysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}".format(**MYSQL_CONFIG)

class BaseConfig(object):
    SQLALCHEMY_RECORD_QUERIES = True

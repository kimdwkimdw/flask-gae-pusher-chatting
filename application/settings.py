"""
settings.py

Configuration for Flask app

Important: Place your keys in the secret_keys.py module,
           which should be kept out of version control.

"""

from secret_keys import CSRF_SECRET_KEY, SESSION_KEY
from user_info import ADMIN_EMAIL, ADMIN_DB_URI


class Config(object):
    # Set secret keys for CSRF protection
    SECRET_KEY = CSRF_SECRET_KEY
    CSRF_SESSION_KEY = SESSION_KEY
    # Flask-Cache settings
    CACHE_TYPE = 'gaememcached'


class Production(Config):
    DEBUG = False
    CSRF_ENABLED = False
    ADMIN = ADMIN_EMAIL
    SQLALCHEMY_DATABASE_URI = ADMIN_DB_URI
    migration_directory = 'migrations'

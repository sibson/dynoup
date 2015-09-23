import os

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['RQ_DEFAULT_URL'] = os.environ.get('REDIS_URL', 'redis://')
app.config['ROLLBAR_ACCESS_TOKEN'] = os.environ.get('ROLLBAR_ACCESS_TOKEN')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgres:///dynoup')
app.config['FERNET_SECRET'] = os.environ['FERNET_SECRET']

db = SQLAlchemy(app)


import utils.requestid  # noqa

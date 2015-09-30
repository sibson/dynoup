import os

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

import structlog
from structlog.stdlib import LoggerFactory
from structlog.threadlocal import wrap_dict


structlog.configure(
    context_class=wrap_dict(dict),
    logger_factory=LoggerFactory(),
)
app = Flask(__name__)

app.config['RQ_DEFAULT_URL'] = os.environ.get('REDIS_URL', 'redis://')
app.config['ROLLBAR_ACCESS_TOKEN'] = os.environ.get('ROLLBAR_ACCESS_TOKEN')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgres:///dynoup')
app.config['FERNET_SECRET'] = os.environ['FERNET_SECRET']

db = SQLAlchemy(app)


import utils.requestid  # noqa

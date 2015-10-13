import os
from datetime import timedelta

from celery import Celery

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

app.config['ROLLBAR_ACCESS_TOKEN'] = os.environ.get('ROLLBAR_ACCESS_TOKEN')

# db
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgres:///dynoup')
app.config['FERNET_SECRET'] = os.environ.get('FERNET_SECRET')

# celery
app.config['CELERY_BROKER_URL'] = os.environ.get('REDIS_URL', 'redis://')
app.config['CELERY_TASK_SERIALIZER'] = 'json'
app.config['CELERYBEAT_SCHEDULE'] = {
    'http-checks': {
        'task': 'scaler.tasks.run_http_checks',
        'schedule': timedelta(minutes=1),
    }
}


db = SQLAlchemy(app)


def make_celery(app):
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery


celery = make_celery(app)


# imports to allow tasks and signals to be registered
import utils.requestid  # noqa
import scaler.tasks  # noqa

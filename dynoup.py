from celery import Celery

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.admin import Admin

import structlog
from structlog.stdlib import LoggerFactory
from structlog.threadlocal import wrap_dict


structlog.configure(
    context_class=wrap_dict(dict),
    logger_factory=LoggerFactory(),
)
app = Flask(__name__)
app.config.from_object('settings')


db = SQLAlchemy(app)
admin = Admin(app, name='DynoUp', template_mode='bootstrap3')


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


# add blueprints
from apiv1.views import api_bp  # noqa
app.register_blueprint(api_bp, url_prefix='/apiv1')


# imports to allow tasks and signals to be registered
import utils.requestid  # noqa
import scaler.tasks  # noqa

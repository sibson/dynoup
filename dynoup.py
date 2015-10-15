from celery import Celery

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.admin import Admin
from flask_marshmallow import Marshmallow


import structlog
from structlog.stdlib import LoggerFactory
from structlog.threadlocal import wrap_dict


structlog.configure(
    context_class=wrap_dict(dict),
    logger_factory=LoggerFactory(),
)
app = Flask(__name__)
app.config.from_object('settings')


admin = Admin(app, name='DynoUp', template_mode='bootstrap3')
db = SQLAlchemy(app)
ma = Marshmallow(app)


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
from apiv2.views import apiv2  # noqa

app.register_blueprint(api_bp, url_prefix='/apiv1')
app.register_blueprint(apiv2)


# imports to allow tasks and signals to be registered
import utils.requestid  # noqa
import scaler.tasks  # noqa

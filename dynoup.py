import os.path

from celery import Celery
from flask import Flask, got_request_exception, request
import rollbar
import rollbar.contrib.flask

import structlog
from structlog.stdlib import LoggerFactory
from structlog.threadlocal import wrap_dict

import settings
from extensions import db, admin
from apiv1.views import apiv1_bp

BLUEPRINTS = (
    apiv1_bp,
)


logger = structlog.get_logger()
celery = Celery(__name__, broker=settings.CELERY_BROKER_URL)


def create_app():
    app = Flask(__name__)
    app.config.from_object('settings')

    configure_extensions(app)
    configure_blueprints(app, BLUEPRINTS)
    configure_logging(app)
    configure_hooks(app)

    return app


def configure_extensions(app):
    db.init_app(app)
    admin.init_app(app)
    celery.conf.update(app.config)


def configure_blueprints(app, blueprints):
    for blueprint in blueprints:
        app.register_blueprint(blueprint)


def configure_logging(app):
    structlog.configure(
        context_class=wrap_dict(dict),
        logger_factory=LoggerFactory(),
    )


def configure_hooks(app):
    @app.before_first_request
    def init_rollbar():
        rollbar.init(
            # access token for the demo app: https://rollbar.com/demo
            app.config['ROLLBAR_ACCESS_TOKEN'],
            # environment name
            'production',
            # server root directory, makes tracebacks prettier
            root=os.path.dirname(os.path.realpath(__file__)),
            # flask already sets up logging
            allow_logging_basic_config=False)

        # send exceptions from `app` to rollbar, using flask's signal system.
        got_request_exception.connect(rollbar.contrib.flask.report_exception, app)

    @app.before_request
    def add_request_id():
        request.id = request.headers.get('X-Request-ID')
        if request.id:
            global logger
            logger = logger.new(request_id=request.id)

# imports to allow tasks
import scaler.tasks  # noqa

import os

import rollbar
import rollbar.contrib.flask
import structlog

from flask import got_request_exception
from flask_restful import Api

import heroku_bouncer


from app import app
from apiv1.apps import AppList, App

logger = structlog.get_logger()


# XXX todo set oauth callback=xyz to create user and get apps
app.wsgi_app = heroku_bouncer.bouncer(app.wsgi_app, scope='write')

api = Api(app)
api.add_resource(AppList, '/apiv1/apps')
api.add_resource(App, '/apiv1/apps/<app_name>')


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


if __name__ == '__main__':
    from structlog.stdlib import LoggerFactory
    from structlog.threadlocal import wrap_dict
    import logging

    structlog.configure(
        context_class=wrap_dict(dict),
        logger_factory=LoggerFactory(),
    )
    logging.basicConfig(level=logging.DEBUG)
    app.run(debug=True)

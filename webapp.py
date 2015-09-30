import os

import rollbar
import rollbar.contrib.flask
import structlog

from flask import got_request_exception
from flask_restful import Api

import heroku_bouncer


from app import app
from apiv1.apps import AppList, App, Check
from scaler.utils import oauth_callback

logger = structlog.get_logger()


app.wsgi_app = heroku_bouncer.bouncer(app.wsgi_app, scope='write', auth_callback=oauth_callback)

api = Api(app)
api.add_resource(AppList, '/apiv1/apps')
api.add_resource(App, '/apiv1/apps/<app_id>')
api.add_resource(Check, '/apiv1/apps/<app_id>/<dynotype>')


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
    import logging

    logging.basicConfig(level=logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True
    app.run(debug=True)

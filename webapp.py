import os

import rollbar
import rollbar.contrib.flask
import structlog

from flask import got_request_exception
from flask_admin import Admin


import heroku_bouncer


from dynoup import app, db
from scaler.utils import oauth_callback

# admin
from scaler import admin as scaler_admin
from scaler import models


import apiv1.urls  # noqa

logger = structlog.get_logger()


app.wsgi_app = heroku_bouncer.bouncer(app.wsgi_app, scope='write', auth_callback=oauth_callback)


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


admin = Admin(app, name='DynoUp', template_mode='bootstrap3')
admin.add_view(scaler_admin.UserAdmin(models.User, db.session))
admin.add_view(scaler_admin.AppAdmin(models.App, db.session))
admin.add_view(scaler_admin.CheckAdmin(models.Check, db.session))


if __name__ == '__main__':
    import logging

    logging.basicConfig(level=logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True
    app.run(debug=True)

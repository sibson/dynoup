import structlog

import heroku_bouncer

from dynoup import create_app
from scaler.utils import oauth_callback

import scaler.admin  # noqa

logger = structlog.get_logger()


app = create_app()
app.wsgi_app = heroku_bouncer.bouncer(app.wsgi_app, scope='write', auth_callback=oauth_callback)


if __name__ == '__main__':
    import logging

    logging.basicConfig(level=logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True
    app.run(debug=True)

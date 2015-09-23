import os

from flask import Flask


app = Flask(__name__)

app.config['RQ_DEFAULT_URL'] = os.environ.get('REDIS_URL', 'redis://')
app.config['ROLLBAR_ACCESS_TOKEN'] = os.environ.get('ROLLBAR_ACCESS_TOKEN')

import utils.requestid  # noqa

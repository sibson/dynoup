import math

import requests
from structlog import get_logger

from scaler.utils import get_heroku_client_for_app

log = get_logger()


def run_check(check):
    response = requests.get(check.url)
    if response.ok:  # maybe scale down?
        log.info('all good', check=check)
        return

    if response.status_code == 503:
        log.info('scaling up', check=check)
        scale_up(check)
        return

    log.error('unexpected response', response=response)


def scale_up(check):
    heroku = get_heroku_client_for_app(check.app)
    app = heroku.apps()[str(check.app.id)]
    formation = app.process_formation()
    dynotype = check.dynotype

    if formation[dynotype].quantity == 0:
        quantity = 1
    else:
        quantity = formation[dynotype].quantity
        quantity = math.ceil(1.20 * quantity)

    app.process_formation()[dynotype].scale(quantity)

    log.info('scaled {}:{}={}'.format(app.name, dynotype, quantity))

import math

import requests
from structlog import get_logger

from dynoup import app, make_celery

from scaler.utils import get_heroku_client_for_app
from scaler.models import Check


log = get_logger()
celery = make_celery(app)


@celery.task()
def run_http_checks():
    for check in Check.query.all():
        run_http_check.delay(check.id)


@celery.task()
def run_http_check(check_id):
    check = Check.query.filter_by(id=check_id).first()
    if not check:
        log.warning('unknown check', id=check_id)
        return

    response = requests.get(check.url)
    if response.ok:  # maybe scale down?
        log.info('all good', check=check)
        return

    if response.status_code == 503:
        log.info('scaling up', check=check)
        scale_up(check)
        return

    log.error('unexpected response', response=response)


@celery.task()
def scale_up(check_id):
    check = Check.query.filter_by(id=check_id).first()
    if not check:
        log.warning('unknown check', id=check_id)
        return

    heroku = get_heroku_client_for_app(check.app)
    app = heroku.apps()[str(check.app.id)]
    formation = app.process_formation()
    dynotype = check.dynotype

    if formation[dynotype].quantity == 0:
        quantity = 1
    else:
        quantity = formation[dynotype].quantity
        quantity = math.ceil(1.20 * quantity)

    app.process_formation()[dynotype].scale(quantity=quantity)
    # TODO log failed scales

    log.info('scaled {}:{}={}'.format(app.name, dynotype, quantity))

    return quantity

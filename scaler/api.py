
from flask import session, request

import heroku3


def apps():
    oauth = request.environ['wsgioauth2.session']
    access_token = oauth['access_token']
    user = oauth['user']

    h = heroku3.from_key(access_token)

    return h.apps()

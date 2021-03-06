from contextlib import contextmanager
import json
import os
import logging
from unittest import TestCase

from flask import appcontext_pushed, g

import responses

from dynoup import app, db
from scaler import models


class HerokuBouncerTestDoubleMiddleWare(object):
    def __init__(self, app):
        self._app = app

    def __call__(self, environ, start_response):
        environ['REMOTE_USER'] = 'testuser@example.com'
        environ['wsgioauth2.session'] = {
                'username': 'testuser@example.com',
                'access_token': 'test-access-token',
                'user': {
                    'email': 'testuser@example.com',
                }
        }

        return self._app(environ, start_response)


class DynoUPTestCase(TestCase):

    def setUp(self):
        logging.basicConfig()
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True

        app.config['FERNET_SECRET'] = 'ovoQLxYEfMnFks8ab7dpHB9RITEaDMaZutxlkHM1TVs='
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///dynoup-test'
        app.config['TESTING'] = True
        app.wsgi_app = HerokuBouncerTestDoubleMiddleWare(app.wsgi_app)

        self.client = app.test_client()

        db.create_all()

        super(DynoUPTestCase, self).setUp()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def add_heroku_response(self, verb, path, filename=None, **kwargs):
        if filename is None:
            filename = 'examples/{}{}.json'.format(verb, path)
        elif not filename.endswith('.json'):
            filename = filename + '.json'

        fh = open(os.path.join('fixtures', filename))
        data = json.loads(fh.read())
        responses.add(verb, 'https://api.heroku.com' + path, json=data, **kwargs)

        return data

    def create_user(self):
        user = models.User(id='01234567-89ab-cdef-0123-456789abcdef', email='testuser@example.com', htoken='testtoken')
        db.session.add(user)
        db.session.commit()

        return user

    def create_app(self):
        app = models.App(id='01234567-89ab-cdef-0123-456789abcdef', name='example')
        db.session.add(app)
        db.session.commit()

        return app

    def create_check(self, app=None):
        check = models.Check(app=app or self.app, url='http://example.com', dynotype='web')
        db.session.add(check)
        db.session.commit()

        return check


@contextmanager
def user_set(app, user):
    def handler(sender, **kwargs):
        g.user = user
    with appcontext_pushed.connected_to(handler, app):
        yield

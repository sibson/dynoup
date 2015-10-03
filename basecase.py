import os
import logging
from unittest import TestCase
import json

import responses

from app import app, db


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
        app.config['FERNET_SECRET'] = 'test'
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///dynoup-test'
        app.config['TESTING'] = True

        logging.basicConfig()
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True

        app.wsgi_app = HerokuBouncerTestDoubleMiddleWare(app.wsgi_app)

        self.client = app.test_client()

        db.create_all()

        super(DynoUPTestCase, self).setUp()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def add_heroku_response(self, verb, path, filename=None, **kwargs):
        if filename is None:
            filename = '{}{}.json'.format(verb, path)

        fh = open(os.path.join('fixtures/examples/', filename))
        data = json.loads(fh.read())
        responses.add(verb, 'https://api.heroku.com' + path, json=data, **kwargs)

        return data

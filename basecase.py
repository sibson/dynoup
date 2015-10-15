from uuid import uuid4
import os
import logging
from unittest import TestCase
import json

import responses

from dynoup import create_app
from extensions import db
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

        app = create_app()
        app.config['FERNET_SECRET'] = 'ovoQLxYEfMnFks8ab7dpHB9RITEaDMaZutxlkHM1TVs='
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///dynoup-test'
        app.config['TESTING'] = True
        app.wsgi_app = HerokuBouncerTestDoubleMiddleWare(app.wsgi_app)

        self.client = app.test_client()

        db.create_all()

        db.session.add(models.User(id=uuid4(), email='testuser@example.com', htoken='testtoken'))
        db.session.commit()

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

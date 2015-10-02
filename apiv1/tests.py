from uuid import uuid4
import json

from basecase import DynoUPTestCase
import responses

from app import db
from apiv1.urls import api  # noqa
from scaler.models import App


class AppTestCase(DynoUPTestCase):

    @responses.activate
    def test_get_list(self):
        self.add_heroku_response(responses.GET, '/account/rate-limits')
        apps = self.add_heroku_response(responses.GET, '/apps')

        response = self.client.get('/apiv1/apps')  # XXX use url_for
        data = json.loads(response.data)

        self.assertEquals(data, {
            apps[0]['name']:  apps[0]['id'],
        })

    @responses.activate
    def test_get_app_no_model(self):
        self.add_heroku_response(responses.GET, '/account/rate-limits')
        apps = self.add_heroku_response(responses.GET, '/apps')
        app = self.add_heroku_response(responses.GET, '/apps/{}'.format(apps[0]['id']))

        response = self.client.get('/apiv1/apps/{}'.format(app['id']))
        data = json.loads(response.data)

        self.assertEquals(data, {
            'name': app['name'],
            'id': app['id'],
            'checks': [],
        })

    def test_get_app_with_checks(self):
        assert False


class CheckTestCase(DynoUPTestCase):

    @responses.activate
    def test_put_check_app_not_in_db(self):
        assert False

    @responses.activate
    def test_put_check_app_in_db(self):
        assert False

    def test_delete_check(self):
        assert False

    def test_get_check(self):
        assert False

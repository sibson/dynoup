import json

from basecase import DynoUPTestCase
import responses

from app import db
from apiv1.urls import api  # noqa
from scaler import models


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
            'checks': {},
        })

    @responses.activate
    def test_get_app_with_checks(self):
        self.add_heroku_response(responses.GET, '/account/rate-limits')
        apps = self.add_heroku_response(responses.GET, '/apps')
        happ = self.add_heroku_response(responses.GET, '/apps/{}'.format(apps[0]['id']))

        dbapp = models.App(id=happ['id'], name=happ['name'])
        db.session.add(dbapp)

        check = models.Check(app_id=dbapp.id, url='http://example.com', dynotype='test')
        db.session.add(check)

        response = self.client.get('/apiv1/apps/{}'.format(dbapp.id))
        data = json.loads(response.data)

        self.assertEquals(data, {
            'name': dbapp.name,
            'id': dbapp.id,
            'checks': {check.dynotype: str(check.id)},
        })


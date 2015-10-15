import json

from flask import url_for

from basecase import DynoUPTestCase
import responses

from dynoup import app


class TestAppListAPI(DynoUPTestCase):

    @responses.activate
    def test_get_list(self):
        self.add_heroku_response(responses.GET, '/account/rate-limits')
        happs = self.add_heroku_response(responses.GET, '/apps')

        with app.test_request_context():
            url = url_for('apiv2.apps')

        response = self.client.get(url)

        data = json.loads(response.data)

        self.assertEquals(len(data['apps']), 1)
        self.assertEquals(data['apps'][0], {
            'id': happs[0]['id'],
            'name': happs[0]['name'],
        })


class TestAppAPI(DynoUPTestCase):
    @responses.activate
    def test_get_app_no_model(self):
        self.add_heroku_response(responses.GET, '/account/rate-limits')
        happs = self.add_heroku_response(responses.GET, '/apps')
        app_id = happs[0]['id']
        happ = self.add_heroku_response(responses.GET, '/apps/{}'.format(app_id))

        with app.test_request_context():
            url = url_for('apiv2.app', app_id=app_id)

        response = self.client.get(url)
        data = json.loads(response.data)

        self.assertEquals(data, {
            'name': happ['name'],
            'id': happ['id'],
        })

    @responses.activate
    def test_get_app_with_checks(self):
        dbapp = self.create_app()
        check = self.create_check(app=dbapp)
        check_id = check.id

        self.add_heroku_response(responses.GET, '/account/rate-limits')
        self.add_heroku_response(responses.GET, '/apps')
        self.add_heroku_response(responses.GET, '/apps/{}'.format(dbapp.id))

        with app.test_request_context():
            url = url_for('apiv2.app', app_id=dbapp.id)

        response = self.client.get(url)
        data = json.loads(response.data)

        self.assertEquals(data, {
            'name': dbapp.name,
            'id': str(dbapp.id),
            'checks': [str(check_id)],
        })

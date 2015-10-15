import json

from basecase import DynoUPTestCase
import responses

from dynoup import db, app
from apiv1.views import api  # noqa
from apiv1.apps import AppList, App, Check
from scaler import models


class TestAppListAPI(DynoUPTestCase):

    @responses.activate
    def test_get_list(self):
        self.add_heroku_response(responses.GET, '/account/rate-limits')
        happs = self.add_heroku_response(responses.GET, '/apps')

        with app.test_request_context():
            url = api.url_for(AppList)

        response = self.client.get(url)

        data = json.loads(response.data)

        self.assertEquals(data, {
            happs[0]['name']:  happs[0]['id'],
        })


class TestAppAPI(DynoUPTestCase):
    @responses.activate
    def test_get_app_no_model(self):
        self.add_heroku_response(responses.GET, '/account/rate-limits')
        happs = self.add_heroku_response(responses.GET, '/apps')
        app_id = happs[0]['id']
        happ = self.add_heroku_response(responses.GET, '/apps/{}'.format(app_id))

        with app.test_request_context():
            url = api.url_for(App, app_id=app_id)

        response = self.client.get(url)
        data = json.loads(response.data)

        self.assertEquals(data, {
            'name': happ['name'],
            'id': happ['id'],
            'checks': {},
        })

    @responses.activate
    def test_get_app_with_checks(self):
        self.add_heroku_response(responses.GET, '/account/rate-limits')
        happs = self.add_heroku_response(responses.GET, '/apps')
        app_id = happs[0]['id']
        happ = self.add_heroku_response(responses.GET, '/apps/{}'.format(app_id))

        with app.test_request_context():
            url = api.url_for(App, app_id=app_id)

        dbapp = models.App(id=app_id, name=happ['name'])
        db.session.add(dbapp)
        check = models.Check(app_id=app_id, url='http://example.com', dynotype='test')
        db.session.add(check)

        response = self.client.get(url)
        data = json.loads(response.data)

        self.assertEquals(data, {
            'name': dbapp.name,
            'id': dbapp.id,
            'checks': {check.dynotype: str(check.id)},
        })


class CheckTestCase(DynoUPTestCase):

    def setUp(self):
        super(CheckTestCase, self).setUp()
        self.app = self.create_app()
        with app.test_request_context():
            self.url = api.url_for(Check, app_id=self.app.id, dynotype='web')

    @responses.activate
    def test_put_check_app_not_in_db(self):
        self.add_heroku_response(responses.GET, '/account/rate-limits')
        self.add_heroku_response(responses.GET, '/apps')
        self.add_heroku_response(responses.GET, '/apps/example/formation')

        db.session.delete(self.app)
        db.session.commit()

        data = {
            'url': 'http://example.com'
        }
        response = self.client.put(self.url, content_type='application/json', data=json.dumps(data))

        self.assertEquals(response.status_code, 201)

        check = models.Check.query.first()

        self.assertEquals(check.url, data['url'])
        self.assertEquals(check.app.name, 'example')
        self.assertEquals(check.app.users.first().email, 'testuser@example.com')

    @responses.activate
    def test_put_check_app_in_db(self):
        self.add_heroku_response(responses.GET, '/account/rate-limits')
        self.add_heroku_response(responses.GET, '/apps')
        self.add_heroku_response(responses.GET, '/apps/example/formation')

        data = {
            'url': 'http://example.com'
        }
        response = self.client.put(self.url, content_type='application/json', data=json.dumps(data))

        self.assertEquals(response.status_code, 201)

        check = models.Check.query.first()

        self.assertEquals(check.url, data['url'])
        self.assertEquals(check.app.name, 'example')
        self.assertEquals(check.app.users.first().email, 'testuser@example.com')

    @responses.activate
    def test_delete_permissions(self):
        self.add_heroku_response(responses.GET, '/account/rate-limits')
        self.add_heroku_response(responses.GET, '/apps', 'apps/empty.json')

        self.create_check()

        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 404)

    @responses.activate
    def test_delete_check(self):
        self.add_heroku_response(responses.GET, '/account/rate-limits')
        self.add_heroku_response(responses.GET, '/apps')

        self.create_check()

        response = self.client.delete(self.url)

        self.assertEquals(response.status_code, 204)
        self.assertIsNone(models.Check.query.first())

    @responses.activate
    def test_get_permissions(self):
        self.add_heroku_response(responses.GET, '/account/rate-limits')
        self.add_heroku_response(responses.GET, '/apps', 'apps/empty.json')

        self.create_check()

        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 404)

    @responses.activate
    def test_get_check(self):
        self.add_heroku_response(responses.GET, '/account/rate-limits')
        self.add_heroku_response(responses.GET, '/apps')

        check = self.create_check()

        response = self.client.get(self.url)

        self.assertEquals(json.loads(response.data), {
            u'id': unicode(check.id),
            u'app_id': unicode(check.app_id),
            u'url': check.url,
            u'dynotype': check.dynotype,
            u'params': {},
        })

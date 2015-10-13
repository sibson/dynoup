import json

from basecase import DynoUPTestCase
import responses

from dynoup import db, app
from apiv1.views import api  # noqa
from apiv1.apps import AppList, App, Check
from scaler import models


class TestAppAPI(DynoUPTestCase):

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
        self.app = models.App(id='01234567-89ab-cdef-0123-456789abcdef', name='example')
        db.session.add(self.app)
        db.session.commit()

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

    def test_delete_check(self):
        check = models.Check(app=self.app, url='http://example.com', dynotype='web')
        db.session.add(check)
        db.session.commit()

        response = self.client.delete(self.url)

        self.assertEquals(response.status_code, 204)
        self.assertIsNone(models.Check.query.first())

    def test_get_check(self):
        check = models.Check(app=self.app, url='http://example.com', dynotype='web')
        db.session.add(check)
        db.session.commit()

        response = self.client.get(self.url)

        check = models.Check.query.first()

        self.assertEquals(json.loads(response.data), {
            u'id': unicode(check.id),
            u'app_id': unicode(check.app_id),
            u'url': check.url,
            u'dynotype': check.dynotype,
            u'params': {},
        })

import json

from flask import url_for

from basecase import DynoUPTestCase
import responses

from dynoup import app, db
from scaler import models


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


class TestCheckAPI(DynoUPTestCase):

    def setUp(self):
        super(TestCheckAPI, self).setUp()
        self.app = self.create_app()
        with app.test_request_context():
            self.url = url_for('apiv2.check', app_id=self.app.id, dynotype='web')

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

import json

from basecase import DynoUPTestCase
import responses

from app import db
from apiv1.urls import api  # noqa
from scaler import models


class TestAppAPI(DynoUPTestCase):

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


class CheckTestCase(DynoUPTestCase):

    def setUp(self):
        super(CheckTestCase, self).setUp()
        self.app = models.App(id='01234567-89ab-cdef-0123-456789abcdef', name='example')
        db.session.add(self.app)
        db.session.commit()

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
        response = self.client.put('apiv1/apps/{}/web'.format(str(self.app.id)),
                                   content_type='application/json', data=json.dumps(data))

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
        response = self.client.put('apiv1/apps/{}/web'.format(str(self.app.id)),
                                   content_type='application/json', data=json.dumps(data))

        self.assertEquals(response.status_code, 201)

        check = models.Check.query.first()

        self.assertEquals(check.url, data['url'])
        self.assertEquals(check.app.name, 'example')
        self.assertEquals(check.app.users.first().email, 'testuser@example.com')

    def test_delete_check(self):
        check = models.Check(app=self.app, url='http://example.com', dynotype='web')
        db.session.add(check)
        db.session.commit()

        response = self.client.delete('/apiv1/apps/{}/web'.format(str(self.app.id)))

        self.assertEquals(response.status_code, 204)
        self.assertIsNone(models.Check.query.first())

    def test_get_check(self):
        check = models.Check(app=self.app, url='http://example.com', dynotype='web')
        db.session.add(check)
        db.session.commit()

        response = self.client.get('/apiv1/apps/{}/web'.format(str(self.app.id)))

        check = models.Check.query.first()

        self.assertEquals(json.loads(response.data), {
            u'id': unicode(check.id),
            u'app_id': unicode(check.app_id),
            u'url': check.url,
            u'dynotype': check.dynotype,
            u'params': {},
        })

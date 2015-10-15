from mock import patch
import responses

from dynoup import db
from scaler import tasks, models, utils

from basecase import DynoUPTestCase


class TestScalerTasks(DynoUPTestCase):
    def setUp(self):
        super(TestScalerTasks, self).setUp()
        self.user = models.User(id='01234567-89ab-cdef-0123-456789abcdef',
                                email='username@example.com')
        self.user.htoken = utils.encrypt_access_token('test-token')
        self.app = models.App(id='01234567-89ab-cdef-0123-456789abcdef', name='example')
        self.app.users.append(self.user)

        self.check = models.Check(app=self.app, dynotype='web', url='http://example.com')
        db.session.add(self.check)
        db.session.commit()

    @responses.activate
    @patch('scaler.tasks.scale_up')
    def test_check_needs_scale_up(self, scale_up):
        responses.add(responses.GET, self.check.url, status=503)
        tasks.run_http_check(self.check.id)
        self.assertTrue(scale_up.call_count)

    @responses.activate
    def test_scale_up(self):
        self.add_heroku_response(responses.GET, '/account/rate-limits')
        self.add_heroku_response(responses.GET, '/apps')
        self.add_heroku_response(responses.GET, '/apps/{}'.format(self.app.id))
        self.add_heroku_response(responses.GET, '/apps/example/formation')

        self.add_heroku_response(responses.PATCH, '/apps/{}/formation/web'.format(self.app.id), 'apps/formation-2')

        quantity = tasks.scale_up(self.check.id)
        self.assertEquals(quantity, 2)

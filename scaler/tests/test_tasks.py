from mock import patch
import responses
from uuid import uuid4

from dynoup import db
from scaler import tasks, models

from basecase import DynoUPTestCase


class TestScalerTasks(DynoUPTestCase):
    def setUp(self):
        super(TestScalerTasks, self).setUp()
        self.app = models.App(id=uuid4(), name='test-app')
        self.check = models.Check(app=self.app, url='http://example.com')
        db.session.add(self.check)
        db.session.commit()

    @responses.activate
    @patch('scaler.tasks.scale_up')
    def test_check_needs_scale_up(self, scale_up):
        responses.add(responses.GET, self.check.url, status=503)
        tasks.run_http_check(self.check.id)
        self.assertTrue(scale_up.call_count)

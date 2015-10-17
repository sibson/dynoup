from dynoup import db
from basecase import DynoUPTestCase

from scaler import models, actions


class TestCreateCheck(DynoUPTestCase):

    def setUp(self):
        super(TestCreateCheck, self).setUp()
        self.app = self.create_app()
        self.user = self.create_user()

    def test_app_exists_in_db(self):
        url = 'http://example.com'
        dynotype = 'test'

        check = actions.CreateCheck.run(self.user, str(self.app.id), self.app.name, dynotype, url)

        self.assertEquals(check.app_id, self.app.id)
        self.assertEquals(check.app.users.first().id, self.user.id)
        self.assertEquals(check.url, url)

        self.assertEquals(self.app.id, models.App.query.first().id)

    def test_app_not_in_db(self):
        db.session.delete(self.app)
        db.session.commit()

        self.test_app_exists_in_db()

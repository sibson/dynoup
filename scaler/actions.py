from dynoup import db

from scaler import models


class CreateCheck(object):

    def __init__(self, user, app_id, app_name, dynotype, url):
        self.user = user
        self.app_id = app_id
        self.app_name = app_name
        self.dynotype = dynotype
        self.url = url

    def __call__(self):
        app, _ = models.App.get_or_create(self.app_id, self.app_name)
        app.users.append(self.user)

        check = models.Check(app_id=self.app_id, dynotype=self.dynotype, url=self.url)

        db.session.add(check)
        db.session.commit()

        return check

from dynoup import db

from scaler import models


class CreateCheck(object):
    @staticmethod
    def run(user, app_id, app_name, dynotype, url):
        app, _ = models.App.get_or_create(app_id, app_name)
        app.users.append(user)

        check = models.Check(app_id=app_id, dynotype=dynotype, url=url)

        db.session.add(check)
        db.session.commit()

        return check

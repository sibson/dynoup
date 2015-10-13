from flask.ext.script import Command

from dynoup import db
from scaler.models import App, User
from scaler.utils import get_heroku_client_for_user


class RefreshApps(Command):
    " Update DB with Apps for all users "

    def run(self):
        for user in User.query.all():
            try:
                client = get_heroku_client_for_user(user)
            except:
                continue

            apps = client.apps()
            for app in apps:
                dbapp = App.query.filter_by(id=app.id).first()
                if not dbapp:
                    dbapp = App(id=app.id, name=app.name)
                    db.session.add(dbapp)
            db.session.commit()

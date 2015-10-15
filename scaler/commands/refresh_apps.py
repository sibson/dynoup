from flask.ext.script import Command, Option

from dynoup import db
from scaler.models import App, User
from scaler.utils import get_heroku_client_for_user


class RefreshApps(Command):
    " Update DB with Apps for all users "

    option_list = (
        Option('users', nargs='*'),
    )

    def run(self, users):
        if users:
            users = User.query.filter(User.email.in_(users))
        else:
            users = User.query.all()

        for user in users:
            print 'Refreshing apps for {}'.format(user.email)
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

#!/usr/bin/env python
import logging

from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

from dynoup import app, db
from scaler import models, tasks

logging.basicConfig(level=logging.DEBUG)

requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

manager = Manager(app)

migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)


@manager.shell
def make_shell_context():
    return dict(app=app, db=db, models=models, tasks=tasks)

if __name__ == '__main__':
    manager.run()

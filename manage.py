#!/usr/bin/env python

from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

from app import app, db

from scaler.models import User


if __name__ == '__main__':
    migrate = Migrate(app, db)

    manager = Manager(app)
    manager.add_command('db', MigrateCommand)
    manager.run()

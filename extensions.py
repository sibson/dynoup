from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.admin import Admin

db = SQLAlchemy()
admin = Admin(name='DynoUp', template_mode='bootstrap3')

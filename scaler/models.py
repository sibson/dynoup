from app import db

from sqlalchemy.dialects.postgresql import UUID


class User(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    htoken = db.Column(db.String(512), nullable=False)


# track many-to-many relationship between apps and users
appusers = db.Table(
    'appusers',
    db.Column('user_id', UUID(as_uuid=True), db.ForeignKey('user.id')),
    db.Column('app_id', UUID(as_uuid=True), db.ForeignKey('app.id'))
)


class App(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True)
    name = db.Column(db.String(128), unique=True)
#    checks = db.relationship('Check', backref=db.backref('app'), lazy='dynamic')
    users = db.relationship('User', secondary=appusers, backref=db.backref('apps'), lazy='dynamic')


#class Check(db.Model):
#    id = db.Column(UUID(as_uuid=True), primary_key=True)
#    app = db.Column('app_id', UUID(as_uuid=True), db.ForeignKey('app.id'))
#    url = db.Column(db.String(256))

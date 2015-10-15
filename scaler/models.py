from uuid import uuid4

from dynoup import db

from sqlalchemy.dialects.postgresql import UUID, JSON


class User(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    htoken = db.Column(db.String(512), nullable=False)

    def __repr__(self):
        return '<User {} ({})>'.format(self.email, self.id)

# track many-to-many relationship between apps and users
appusers = db.Table(
    'appusers',
    db.Column('user_id', UUID(as_uuid=True), db.ForeignKey('user.id')),
    db.Column('app_id', UUID(as_uuid=True), db.ForeignKey('app.id'))
)


class App(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True)
    name = db.Column(db.String(128), unique=True)
    users = db.relationship('User', secondary=appusers, backref=db.backref('app'), lazy='dynamic')
    checks = db.relationship('Check', backref=db.backref('app'), lazy='dynamic')

    def __repr__(self):
        return '<App {} ({})>'.format(self.name, self.id)

    @classmethod
    def get_or_create(cls, app_id, name=None):
        instance = cls.query.filter_by(id=app_id).first()
        if instance:
            return instance, False

        instance = cls(id=app_id, name=name)
        db.session.add(instance)
        db.session.commit()

        return instance, True


class Check(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    app_id = db.Column(UUID(as_uuid=True), db.ForeignKey('app.id'))
    url = db.Column(db.String(256))
    dynotype = db.Column(db.String(64))
    params = db.Column(JSON(), default={})

    def __repr__(self):
        return '<Check {}/{} {}>'.format(self.app.name, self.dynotype, self.url)

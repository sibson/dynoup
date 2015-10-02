from flask import request
from flask_restful import Resource, abort, marshal_with, fields

from app import db
from scaler.utils import get_heroku_client_for_session
from scaler import models


class AppList(Resource):
    def get(self):
        heroku = get_heroku_client_for_session()
        return {a.name: a.id for a in heroku.apps()}


class App(Resource):
    def get(self, app_id):
        app = models.App.query.filter_by(id=app_id).first()

        if app:
            checks = {c.dynotype: str(c.id) for c in app.checks}
        else:
            checks = []

            heroku = get_heroku_client_for_session()
            apps = heroku.apps()
            if app_id not in apps:
                abort(404, message="App {} doesn't exist".format(app_id))

            app = apps[app_id]

        return {
            'name': app.name,
            'id': app_id,
            'checks': checks,
        }


check_fields = {
    'id': fields.String,
    'app_id': fields.String,
    'url': fields.String,
    'dynotype': fields.String,
    'params': fields.String,
}


class Check(Resource):
    @marshal_with(check_fields)
    def put(self, app_id, dynotype):
        heroku = get_heroku_client_for_session()
        try:
            app = heroku.apps()[app_id]
        except KeyError:
            abort(404, message="App {} doesn't exist".format(app_id))

        try:
            app.process_formation()[dynotype]
        except KeyError:
            abort(404, message="Dynotype {} doesn't exist".format(dynotype))

        dbapp = models.App.query.filter_by(id=app_id).first()
        if not dbapp:
            dbapp = models.App(id=app_id, name=app.name)
            db.session.add(dbapp)

        # middleware?
        email = request.environ['REMOTE_USER']
        user = models.User.query.filter_by(email=email).first()
        dbapp.users.append(user)

        url = request.json['url']
        check = models.Check(app_id=app.id, dynotype=dynotype, url=url)

        # XXX need to add check to session?
        db.session.add(check)
        db.session.commit()

        return check, 201

    @marshal_with(check_fields)
    def get(self, app_id, dynotype):
        # XXX permissions
        check = models.Check.query.filter_by(app_id=app_id, dynotype=dynotype).first()
        if not check:
            abort(404, message="Check {}:{} doesn't exist".format(app_id, dynotype))

        return check

    def delete(self, app_id, dynotype):
        # XXX permissions
        check = models.Check.query.filter_by(app_id=app_id, dynotype=dynotype).first()
        if not check:
            abort(404, message="Check {}:{} doesn't exist".format(app_id, dynotype))

        db.session.delete(check)
        db.session.commit()

        return {}, 204

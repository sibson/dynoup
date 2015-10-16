from flask import request
from flask_restful import Resource, abort, marshal_with, fields, reqparse

from dynoup import db
from apiv1.views import api
from scaler.utils import get_heroku_client_for_session
from scaler import models, actions


class AppList(Resource):
    def get(self):
        heroku = get_heroku_client_for_session()
        return {a.name: a.id for a in heroku.apps()}
api.add_resource(AppList, '/apps')


class App(Resource):
    def get(self, app_id):

        heroku = get_heroku_client_for_session()
        apps = heroku.apps()  # getto permissions check
        if app_id not in apps:
            abort(404, message="App {} doesn't exist".format(app_id))

        app = models.App.query.filter_by(id=app_id).first()
        if app:
            checks = {c.dynotype: str(c.id) for c in app.checks}
        else:
            app = apps[app_id]
            checks = {}

        return {
            'name': app.name,
            'id': app_id,
            'checks': checks,
        }
api.add_resource(App, '/apps/<app_id>')


check_fields = {
    'id': fields.String,
    'app_id': fields.String,
    'url': fields.String,
    'dynotype': fields.String,
    'params': fields.Raw,
}


def get_app_or_404(app_id):
    heroku = get_heroku_client_for_session()
    try:
        app = heroku.apps()[app_id]
    except KeyError:
        abort(404, message="App {} doesn't exist".format(app_id))

    return app


class Check(Resource):
    decorators = []  # XXX add permissions

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('url', type=str, required=True,
                                   help='missing URL to check', location='json')

    @marshal_with(check_fields)
    def put(self, app_id, dynotype):
        app = get_app_or_404(app_id)
        try:
            app.process_formation()[dynotype]
        except KeyError:
            abort(404, message="Dynotype {} doesn't exist".format(dynotype))

        args = self.reqparse.parse_args()

        # XXX middleware
        email = request.environ['REMOTE_USER']
        user = models.User.query.filter_by(email=email).first()

        check = actions.CreateCheck(user, app_id, app.name, dynotype, args['url'])()

        return check, 201

    @marshal_with(check_fields)
    def get(self, app_id, dynotype):
        get_app_or_404(app_id)  # getto permission check
        check = models.Check.query.filter_by(app_id=app_id, dynotype=dynotype).first()
        if not check:
            abort(404, message="Check {}:{} doesn't exist".format(app_id, dynotype))

        return check

    def delete(self, app_id, dynotype):
        get_app_or_404(app_id)  # getto permission check
        check = models.Check.query.filter_by(app_id=app_id, dynotype=dynotype).first()
        if not check:
            abort(404, message="Check {}:{} doesn't exist".format(app_id, dynotype))

        db.session.delete(check)
        db.session.commit()

        return {}, 204
api.add_resource(Check, '/apps/<app_id>/<dynotype>')

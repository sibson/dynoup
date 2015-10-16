from flask import Blueprint, jsonify, request
from flask.views import MethodView

from dynoup import db
from scaler import models, utils, actions
from apiv2.schemas import AppSchema, CheckSchema
from apiv2.errors import NotFoundError


apiv2 = Blueprint('apiv2', __name__, url_prefix='/apiv2')


@apiv2.route('/apps')
def apps():
    heroku = utils.get_heroku_client_for_session()
    apps = heroku.apps()
    return jsonify({'apps': AppSchema(many=True).dump(apps).data})


@apiv2.route('/apps/<app_id>')
def app(app_id):
    heroku = utils.get_heroku_client_for_session()
    apps = heroku.apps()  # getto permissions check

    if app_id not in apps:
        raise NotFoundError('app', app_id)

    app = models.App.query.filter_by(id=app_id).first()
    if not app:
        app = apps[app_id]

    return AppSchema().jsonify(app)


class CheckAPI(MethodView):
    decorators = []  # XXX add permissions

    def get_app(self, app_id):
        heroku = utils.get_heroku_client_for_session()
        try:
            app = heroku.apps()[app_id]
        except KeyError:
            raise NotFoundError('app', app_id)

        return app

    def get_check(self, app_id, dynotype):
        self.get_app(app_id)  # getto permissions check
        check = models.Check.query.filter_by(app_id=app_id, dynotype=dynotype).first()
        if not check:
            raise NotFoundError('check', '{}:{}'.format(app_id, dynotype))

        return check

    def jsonify(self, check):
        return CheckSchema().jsonify(check)

    def get(self, app_id, dynotype):
        check = self.get_check(app_id, dynotype)
        return self.jsonify(check)

    def delete(self, app_id, dynotype):
        check = self.get_check(app_id, dynotype)
        db.session.delete(check)
        db.session.commit()

        return jsonify({}), 204

    def put(self, app_id, dynotype):
        app = self.get_app(app_id)  # getto permissions check

        data, errors = CheckSchema().load(request.get_json())
        if errors:
            return jsonify(errors), 422

        # XXX middleware? flask-login?
        email = request.environ['REMOTE_USER']
        user = models.User.query.filter_by(email=email).first()

        check = actions.CreateCheck(user, app_id, app.name, dynotype, data['url'])()

        return self.jsonify(check), 201

check_view = CheckAPI.as_view('check')
apiv2.add_url_rule('/apps/<app_id>/checks/<dynotype>',
                   view_func=check_view,
                   methods=['PUT', 'GET', 'DELETE'])

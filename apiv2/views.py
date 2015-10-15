from flask import Blueprint, abort, jsonify

from scaler import models, utils
from apiv2.schemas import AppSchema


apiv2 = Blueprint('apiv2', __name__, url_prefix='/apiv2')


@apiv2.route('/apps')
def apps():
    heroku = utils.get_heroku_client_for_session()
    apps = heroku.apps()
    schema = AppSchema(many=True)
    return jsonify({'apps': schema.dump(apps).data})


@apiv2.route('/apps/<app_id>')
def app(app_id):
    heroku = utils.get_heroku_client_for_session()
    apps = heroku.apps()  # getto permissions check

    if app_id not in apps:
        abort(404, message="App {} doesn't exist".format(app_id))

    app = models.App.query.filter_by(id=app_id).first()
    if not app:
        app = apps[app_id]

    app_schema = AppSchema()
    return app_schema.jsonify(app)

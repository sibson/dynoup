from flask import Blueprint

from flask_restful import Api

from apiv1.apps import AppList, App, Check

bp = Blueprint('apiv1', __name__)

api = Api(bp)
api.add_resource(AppList, '/apps')
api.add_resource(App, '/apps/<app_id>')
api.add_resource(Check, '/apps/<app_id>/<dynotype>')

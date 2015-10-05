from flask_restful import Api

from apiv1.apps import AppList, App, Check
from dynoup import app

api = Api(app)
api.add_resource(AppList, '/apiv1/apps')
api.add_resource(App, '/apiv1/apps/<app_id>')
api.add_resource(Check, '/apiv1/apps/<app_id>/<dynotype>')

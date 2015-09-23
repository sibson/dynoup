from flask_restful import Resource, abort

from scaler.api import apps


class AppList(Resource):
    def get(self):
        return [a.name for a in apps()]


class App(Resource):
    def get(self, app_name):
        try:
            app = apps()[app_name]
        except KeyError:
            abort('404', message="App {} doesn't exist".format(app_name))

        return {f.type: f.quantity for f in app.process_formation()}

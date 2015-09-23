from flask_restful import Resource, abort

from scaler.utils import get_heroku_client_for_session


class AppList(Resource):
    def get(self):
        heroku = get_heroku_client_for_session()
        return [a.name for a in heroku.apps()]


class App(Resource):
    def get(self, app_name):
        heroku = get_heroku_client_for_session()
        try:
            app = heroku.apps()[app_name]
        except KeyError:
            abort('404', message="App {} doesn't exist".format(app_name))

        return {f.type: f.quantity for f in app.process_formation()}

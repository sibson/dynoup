from flask import jsonify

from dynoup import app


class APIError(Exception):
    def __init__(self, status_code=None, *args, **kwargs):
        super(Exception, self).__init__(*args, **kwargs)
        self.status_code = status_code or 500
        self.message = 'Unknown'

    def to_dict(self):
        return {
            'message': self.message
        }


class NotFoundError(APIError):
    def __init__(self, name, ident):
        super(NotFoundError, self).__init__(status_code=404)
        self.message = '{} {} does not exist'.format(name, ident)


@app.errorhandler(APIError)
def handle_api_error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

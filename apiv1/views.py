from flask import Blueprint
from flask_restful import Api

api_bp = Blueprint('apiv1', __name__)
api = Api(api_bp)

# allow resources to be discovered
import apiv1.apps  # noqa

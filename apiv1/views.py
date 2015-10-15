from flask import Blueprint
from flask_restful import Api

apiv1_bp = Blueprint('apiv1', __name__, url_prefix='/apiv1')  # url_prefix in "app"
api = Api(apiv1_bp)

# allow resources to be discovered
import apiv1.apps  # noqa

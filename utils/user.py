from flask import request, g

from dynoup import app
from scaler.models import User


@app.before_request
def attach_current_user():
    g.user = User.query.filter_by(email=request.environ['REMOTE_USER']).first()

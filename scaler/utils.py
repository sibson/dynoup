from cryptography.fernet import Fernet, InvalidToken

from flask import request
import heroku3
import structlog

from app import app, db
from scaler.models import User


logger = structlog.get_logger()


def oauth_callback(token):
    user = User.query.filter_by(email=token['username']).first()

    if not user:
        user = User(id=token['user_id'], email=token['username'])

    fernet = Fernet(app.config['FERNET_SECRET'])
    user.htoken = fernet.encrypt(token.access_token.encode('utf-8')).decode('utf-8')
    db.session.add(user)
    db.session.commit()

    return True


def get_heroku_token_for_session():
    oauth = request.environ['wsgioauth2.session']
    access_token = oauth['access_token']

    return access_token


def get_heroku_client(access_token):
    return heroku3.from_key(access_token)


def get_heroku_client_for_session():
    return get_heroku_client(get_heroku_token_for_session())


def get_valid_heroku_client_for(app):
    for user in app.users:
        try:
            fernet = Fernet(app.config['FERNET_SECRET'])
            token = fernet.decrypt(user.htoken.encode('utf-8')).decode('utf-8')
        except (InvalidToken, IndexError):
            logger.exception('invalid token')
            continue

        client = get_heroku_client(token)
        try:
            client.apps()
        except Exception:
            # XXX narrow the execption
            logger.exception('failed to access Heroku')
            continue

        return client

    raise Exception('unable to access heroku')

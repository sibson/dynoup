from cryptography.fernet import Fernet, InvalidToken

from flask import request
import heroku3
import structlog

from dynoup import app, db
from scaler.models import User, App


logger = structlog.get_logger()


def oauth_callback(token):
    """ Called after successful OAuth with Heroku

    We need to capture the Heroku access_token for the User
    """

    user = User.query.filter_by(email=token['username']).first()
    if not user:
        user = User(id=token['user_id'], email=token['username'])

    fernet = Fernet(app.config['FERNET_SECRET'])
    user.htoken = fernet.encrypt(token.access_token.encode('utf-8')).decode('utf-8')
    db.session.add(user)

    # link all apps to the user
    heroku = get_heroku_client(token.access_token)
    for happ in heroku.apps():
        dbapp = App.query.filter_by(id=happ.id, name=happ.name).first()
        if dbapp:
            dbapp.users.append(user)
            db.session.add(dbapp)

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


def get_heroku_client_for_app(dbapp):
    fernet = Fernet(app.config['FERNET_SECRET'])
    for user in dbapp.users.all():
        try:
            token = fernet.decrypt(user.htoken.encode('utf-8')).decode('utf-8')
        except (InvalidToken, IndexError):
            logger.exception('invalid token')
            continue

        client = get_heroku_client(token)
        try:
            client.apps()[dbapp.name]
        except Exception:
            # XXX narrow the execption
            logger.exception('failed to access Heroku')
            continue

        return client

    raise Exception('no users with access to app')

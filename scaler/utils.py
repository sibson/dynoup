from cryptography.fernet import Fernet, InvalidToken

from flask import request
import heroku3
import structlog

from dynoup import app, db
from scaler.models import User, App


logger = structlog.get_logger()


def encrypt_access_token(access_token):
    fernet = Fernet(app.config['FERNET_SECRET'])
    return fernet.encrypt(access_token.encode('utf-8')).decode('utf-8')


def oauth_callback(token):
    """ Called after successful OAuth with Heroku

    We need to capture the Heroku access_token for the User
    """

    user = User.query.filter_by(email=token['username']).first()
    if not user:
        user = User(id=token['user_id'], email=token['username'])
    user.htoken = encrypt_access_token(token.access_token)
    db.session.add(user)

    # link all apps to the user
    heroku = get_heroku_client(token.access_token)
    for happ in heroku.apps():
        dbapp = App.query.filter_by(id=happ.id, name=happ.name).first()
        if dbapp:
            dbapp.users.append(user)
            db.session.add(dbapp)

    db.session.commit()

    return user


def get_heroku_token_for_session():
    oauth = request.environ['wsgioauth2.session']
    access_token = oauth['access_token']

    return access_token


def get_heroku_client(access_token):
    return heroku3.from_key(access_token)


def get_heroku_client_for_session():
    return get_heroku_client(get_heroku_token_for_session())


def get_heroku_client_for_user(user):
    fernet = Fernet(app.config['FERNET_SECRET'])
    try:
        token = fernet.decrypt(user.htoken.encode('utf-8')).decode('utf-8')
    except (InvalidToken, IndexError):
        logger.exception('invalid token')
        raise

    return get_heroku_client(token)


def get_heroku_client_for_app(dbapp):
    for user in dbapp.users.all():
        try:
            client = get_heroku_client_for_user(user)
        except (InvalidToken, IndexError):
            continue

        try:
            client.apps()[dbapp.name]
        except Exception:
            # XXX narrow the execption
            logger.exception('failed to access Heroku')
            continue

        return client

    raise Exception('no users with access to app')

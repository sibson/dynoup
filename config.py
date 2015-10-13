import os
from datetime import timedelta

ROLLBAR_ACCESS_TOKEN = os.environ.get('ROLLBAR_ACCESS_TOKEN')


SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgres:///dynoup')
FERNET_SECRET = os.environ.get('FERNET_SECRET')


CELERY_BROKER_URL = os.environ.get('REDIS_URL', 'redis://')
CELERY_TASK_SERIALIZER = 'json'
CELERYBEAT_SCHEDULE = {
    'http-checks': {
        'task': 'scaler.tasks.run_http_checks',
        'schedule': timedelta(minutes=1),
    }
}

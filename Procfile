web: gunicorn webapp:app --log-file=-
worker: celery -A dynoup.celery --beat worker

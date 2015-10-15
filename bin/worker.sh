celery -A worker.celery --beat --loglevel=debug worker $@

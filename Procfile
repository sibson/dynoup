web: gunicorn webapp:app --log-file=-
worker: python rqworker.py
testapp: gunicorn testapp:app --log-file=-

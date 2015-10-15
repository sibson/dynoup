#!/usr/bin/env python

from dynoup import celery, create_app  # noqa

app = create_app()
app.app_context().push()

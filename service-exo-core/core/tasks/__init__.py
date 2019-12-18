from celery import current_app as app

from .instrumentation import InstrumentationTask


app.tasks.register(InstrumentationTask())

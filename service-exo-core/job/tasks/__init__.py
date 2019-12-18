from celery import current_app as app

from .core_job import (
    CoreJobCreate,
    CoreJobUpdate,
    CoreJobDelete,
)


app.tasks.register(CoreJobCreate())
app.tasks.register(CoreJobUpdate())
app.tasks.register(CoreJobDelete())

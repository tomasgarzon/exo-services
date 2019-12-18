from celery import current_app as app

from .participant import (
    JobCreate, JobUpdate, JobDelete,
    EventOpportunityJobUpdate)

app.tasks.register(JobCreate())
app.tasks.register(JobUpdate())
app.tasks.register(JobDelete())
app.tasks.register(EventOpportunityJobUpdate())

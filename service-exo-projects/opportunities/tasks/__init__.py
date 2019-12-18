from celery import current_app as app

from .opportunity_group import (
    OpportunityGroupCreateTask,
    OpportunityGroupUpdateTask, OpportunityGroupDeleteTask)


app.tasks.register(OpportunityGroupCreateTask())
app.tasks.register(OpportunityGroupUpdateTask())
app.tasks.register(OpportunityGroupDeleteTask())

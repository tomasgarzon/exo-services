from celery import current_app as app

from .group import (
    GroupCreateTask, GroupUpdateTask, GroupDeleteTask)


app.tasks.register(GroupCreateTask())
app.tasks.register(GroupUpdateTask())
app.tasks.register(GroupDeleteTask())

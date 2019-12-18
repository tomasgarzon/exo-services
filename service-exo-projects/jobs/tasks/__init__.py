from celery import current_app as app


from .user_project_role import (
    ProjectJobCreate, ProjectJobUpdate, ProjectJobDelete,
    ProjectOpportunityJobUpdate)

app.tasks.register(ProjectJobCreate())
app.tasks.register(ProjectJobUpdate())
app.tasks.register(ProjectJobDelete())
app.tasks.register(ProjectOpportunityJobUpdate())

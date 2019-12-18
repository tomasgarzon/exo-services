from celery import current_app as app

from .project_location import ProjectLocationTask
from .project_populate import ProjectPopulateTask
from .project_launch import ProjectLaunchTask
from .project_media_library import AssignResourcesToProjectTask
from .project_emails import (
    ProjectLocationChangedTask,
    ProjectStartChangedTask,
    StepStartChangedTask,
    MemberAddedTeamTask,
    MemberRemovedTask,
    RolesChangedTask)


app.tasks.register(ProjectLocationTask())
app.tasks.register(ProjectPopulateTask())
app.tasks.register(ProjectLaunchTask())
app.tasks.register(AssignResourcesToProjectTask())
app.tasks.register(ProjectLocationChangedTask())
app.tasks.register(ProjectStartChangedTask())
app.tasks.register(StepStartChangedTask())
app.tasks.register(MemberAddedTeamTask())
app.tasks.register(MemberRemovedTask())
app.tasks.register(RolesChangedTask())

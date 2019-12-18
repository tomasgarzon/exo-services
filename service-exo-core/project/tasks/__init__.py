from celery import current_app as app

from .media_library import AssignResourcesToProjectTask, AssignProjectToResourceTask
from .project_status import StartProjectTask, FinishProjectTask
from .project_conversations import CreateConversationProjectTask


app.tasks.register(AssignResourcesToProjectTask())
app.tasks.register(AssignProjectToResourceTask())
app.tasks.register(StartProjectTask())
app.tasks.register(FinishProjectTask())
app.tasks.register(CreateConversationProjectTask())

from service.celery import app

from .exo_website import (
    CreateWorkshopWebsiteTask,
    DeleteWorkshopWebsiteTask,
)
from .events_tasks import (
    EventUpdatedOwnerNotificationTask,
    NotifyEventManagerTask,
    SummitRequestTask,
)
from .sync_participant_task import SyncParticipantTask
from .workshop_reminder_task import WorkshopReminderTask


app.tasks.register(EventUpdatedOwnerNotificationTask())
app.tasks.register(NotifyEventManagerTask())
app.tasks.register(SummitRequestTask())
app.tasks.register(CreateWorkshopWebsiteTask())
app.tasks.register(DeleteWorkshopWebsiteTask())
app.tasks.register(SyncParticipantTask())
app.tasks.register(WorkshopReminderTask())

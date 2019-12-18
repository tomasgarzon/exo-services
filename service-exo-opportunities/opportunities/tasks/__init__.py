from service.celery import app
from .new_opportunity import NewOpportunityTask
from .opportunity_assigned import OpportunitySelectedTask
from .opportunity_not_assigned import OpportunityNotSelectedTask
from .new_applicant import NewApplicantTask
from .conversations import CreateOportunityConversationTask
from .opportunity_removed import OpportunityRemovedTask
from .opportunity_edited import OpportunityEditedTask
from .opportunity_closed_by_positions import OpportunityClosedByPositionTask
from .opportunity_closed import OpportunityClosedTask
from .opportunity_closed_deadline import OpportunityClosedDeadlineTask
from .conversations_add_message import AddMessageToConversationTask
from .conversation_message import OpportunityMessageReceivedTask
from .opportunity_feedback_requested import OpportunityFeedackRequestedTask
from .opportunity_feedback_reminder import (
    OpportunityFeedackReminderRequesterTask,
    OpportunityFeedackReminderApplicantTask)
from .opportunity_feedback_expired import (
    OpportunityFeedackExpiredRequesterTask,
    OpportunityFeedackExpiredApplicantTask,
    )
from .opportunity_feedback_left import (
    OpportunityApplicantLeftFeedbackTask,
    OpportunityRequesterLeftFeedbackTask)


app.tasks.register(NewOpportunityTask())
app.tasks.register(OpportunitySelectedTask())
app.tasks.register(OpportunityNotSelectedTask())
app.tasks.register(NewApplicantTask())
app.tasks.register(CreateOportunityConversationTask())
app.tasks.register(OpportunityRemovedTask())
app.tasks.register(OpportunityEditedTask())
app.tasks.register(OpportunityClosedTask())
app.tasks.register(OpportunityClosedByPositionTask())
app.tasks.register(OpportunityClosedDeadlineTask())
app.tasks.register(AddMessageToConversationTask())
app.tasks.register(OpportunityMessageReceivedTask())
app.tasks.register(OpportunityFeedackRequestedTask())
app.tasks.register(OpportunityFeedackReminderApplicantTask())
app.tasks.register(OpportunityFeedackReminderRequesterTask())
app.tasks.register(OpportunityFeedackExpiredRequesterTask())
app.tasks.register(OpportunityFeedackExpiredApplicantTask())
app.tasks.register(OpportunityApplicantLeftFeedbackTask())
app.tasks.register(OpportunityRequesterLeftFeedbackTask())

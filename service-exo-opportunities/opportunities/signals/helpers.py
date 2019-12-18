from django.conf import settings

from ..tasks import (
    OpportunityNotSelectedTask,
    OpportunityClosedTask,
    OpportunityClosedByPositionTask,
    OpportunityClosedDeadlineTask,
)


def send_email_when_opportunity_is_closed(opportunity, user_list, origin, comment=None):
    if origin == settings.OPPORTUNITIES_CH_CLOSE_MANUALLY:
        for user in user_list:
            OpportunityClosedTask().s(
                pk=opportunity.pk,
                user_pk=user.pk,
                comment=comment).apply_async()
    elif origin == settings.OPPORTUNITIES_CH_CLOSE_POSITIONS:
        for user in user_list:
            OpportunityNotSelectedTask().s(
                pk=opportunity.pk,
                user_pk=user.pk).apply_async()
        OpportunityClosedByPositionTask().s(
            pk=opportunity.pk).apply_async()
    elif origin == settings.OPPORTUNITIES_CH_CLOSE_DEADLINE:
        for user in user_list:
            OpportunityClosedTask().s(
                pk=opportunity.pk,
                user_pk=user.pk).apply_async()
        OpportunityClosedDeadlineTask().s(
            pk=opportunity.pk).apply_async()

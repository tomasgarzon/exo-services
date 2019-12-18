from django.conf import settings

from actstream.actions import unfollow

from ..tasks import (
    NewOpportunityTask,
    OpportunitySelectedTask,
    OpportunityRemovedTask,
    OpportunityEditedTask,
    NewApplicantTask,
    OpportunityApplicantLeftFeedbackTask,
    OpportunityRequesterLeftFeedbackTask,
    OpportunityNotSelectedTask,
)
from .helpers import send_email_when_opportunity_is_closed
from ..signals_define import opportunity_positions_covered


def opportunity_send_handler(sender, opportunity, *args, **kwargs):
    if not settings.POPULATOR_MODE:
        NewOpportunityTask().s(pk=opportunity.pk).apply_async()


def opportunity_send_to_user_handler(sender, opportunity, user, *args, **kwargs):
    if not settings.POPULATOR_MODE:
        NewOpportunityTask().s(
            pk=opportunity.pk,
            user_pk=user.pk).apply_async()


def opportunity_selected_handler(sender, opportunity, applicant, *args, **kwargs):
    if not settings.POPULATOR_MODE:
        OpportunitySelectedTask().s(
            pk=opportunity.pk,
            applicant_pk=applicant.pk).apply_async()

    if opportunity.num_positions == opportunity.applicants_info.filter_by_status_selected().count():
        opportunity_positions_covered.send(
            sender=opportunity.__class__, opportunity=opportunity)


def opportunity_closed_handler(sender, opportunity, user_list, origin, *args, **kwargs):
    if not settings.POPULATOR_MODE:
        send_email_when_opportunity_is_closed(
            opportunity, user_list, origin, kwargs.get('comment'))
    for user in user_list:
        unfollow(user, opportunity)


def new_applicant_handler(sender, opportunity, applicant, *args, **kwargs):
    if not settings.POPULATOR_MODE:
        NewApplicantTask().s(
            pk=opportunity.pk,
            applicant_pk=applicant.pk,
        ).apply_async()


def opportunity_removed_handler(sender, opportunity, comment, *args, **kwargs):
    if not settings.POPULATOR_MODE:
        OpportunityRemovedTask().s(
            pk=opportunity.pk,
            comment=comment).apply_async()


def opportunity_edited_handler(
        sender, opportunity, comment, send_notification,
        *args, **kwargs):
    if not settings.POPULATOR_MODE and send_notification:
        OpportunityEditedTask().s(
            pk=opportunity.pk,
            comment=comment).apply_async()
    target_change = kwargs.get('target_change')
    users_tagged_change = kwargs.get('users_tagged_change')
    opportunity.update_target_and_users(
        target_change, users_tagged_change)


def opportunity_positions_covered_handler(sender, opportunity, *args, **kwargs):
    opportunity.close_by_positions_covered()


def opportunity_applicant_feedback_left(sender, opportunity, applicant, user_from, *args, **kwargs):
    if not settings.POPULATOR_MODE:
        if opportunity.created_by == user_from:
            OpportunityRequesterLeftFeedbackTask().s(
                pk=opportunity.pk,
                applicant_pk=applicant.pk).apply_async()
        elif applicant.user == user_from:
            OpportunityApplicantLeftFeedbackTask().s(
                pk=opportunity.pk,
                applicant_pk=applicant.pk).apply_async()


def opportunity_rejected_handler(sender, opportunity, applicant, *args, **kwargs):
    if not settings.POPULATOR_MODE:
        OpportunityNotSelectedTask().s(
            pk=opportunity.pk,
            user_pk=applicant.user.pk).apply_async()

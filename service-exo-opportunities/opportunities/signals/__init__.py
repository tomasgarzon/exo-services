from django.apps import apps
from django.db.models.signals import (
    post_migrate, post_save, post_delete)

from ..signals_define import (
    opportunity_post_send,
    opportunity_send_to_user,
    opportunity_post_selected,
    opportunity_post_rejected,
    opportunity_post_closed,
    opportunity_post_removed,
    opportunity_post_edited,
    opportunity_new_applicant,
    opportunity_positions_covered,
    send_message_to_conversation,
    signal_create_new_conversation,
    opportunity_feedback_left)

from .opportunity_change_status import (
    opportunity_send_handler,
    opportunity_send_to_user_handler,
    opportunity_selected_handler,
    opportunity_rejected_handler,
    opportunity_closed_handler,
    opportunity_removed_handler,
    opportunity_edited_handler,
    opportunity_positions_covered_handler,
    new_applicant_handler,
    opportunity_applicant_feedback_left)
from .job import (
    post_applicant_sow_save_handler,
    post_applicant_sow_delete_handler)
from . import conversations
from .permissions import post_migrate_create_user_permissions


def setup_signals():
    Opportunity = apps.get_model('opportunities', 'Opportunity')
    Applicant = apps.get_model('opportunities', 'Applicant')
    ApplicantSow = apps.get_model('opportunities', 'ApplicantSow')
    UserTagged = apps.get_model('opportunities', 'UserTagged')

    opportunity_post_send.connect(opportunity_send_handler)
    opportunity_send_to_user.connect(
        opportunity_send_to_user_handler)
    opportunity_post_selected.connect(opportunity_selected_handler)
    opportunity_post_rejected.connect(
        opportunity_rejected_handler)
    opportunity_post_closed.connect(opportunity_closed_handler)
    opportunity_post_removed.connect(opportunity_removed_handler)
    opportunity_post_edited.connect(opportunity_edited_handler)

    opportunity_new_applicant.connect(new_applicant_handler)
    opportunity_new_applicant.connect(
        conversations.start_converation_for_applicant_handler)
    signal_create_new_conversation.connect(
        conversations.start_conversation_handler, sender=Opportunity)
    send_message_to_conversation.connect(
        conversations.send_message_to_conversation_handler,
        sender=Applicant)

    post_migrate.connect(post_migrate_create_user_permissions)

    opportunity_positions_covered.connect(
        opportunity_positions_covered_handler,
        sender=Opportunity)

    opportunity_feedback_left.connect(
        opportunity_applicant_feedback_left,
        sender=Applicant)

    post_save.connect(
        conversations.create_conversation_for_user_tagged,
        sender=UserTagged)

    post_save.connect(
        post_applicant_sow_save_handler,
        sender=ApplicantSow)
    post_delete.connect(
        post_applicant_sow_delete_handler,
        sender=ApplicantSow)

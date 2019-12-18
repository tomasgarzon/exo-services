from django.conf import settings

from ..tasks import CreateOportunityConversationTask, AddMessageToConversationTask


def start_conversation_handler(opportunity, user_from, message, files, *args, **kwargs):
    if settings.POPULATOR_MODE:
        return
    data = {
        'opportunity_id': opportunity.id,
        'user_from_id': user_from.pk,
        'message': message,
        'files': files,
    }
    if kwargs.get('user_to'):
        data['user_to_id'] = kwargs.get('user_to').id
    CreateOportunityConversationTask().s(**data).apply_async()


def start_converation_for_applicant_handler(sender, opportunity, applicant, *args, **kwargs):
    if settings.POPULATOR_MODE:
        return

    data = {
        'opportunity_id': opportunity.id,
        'user_from_id': applicant.user.id,
        'message': '',
        'files': [],
    }

    CreateOportunityConversationTask().s(**data).apply_async()


def send_message_to_conversation_handler(sender, applicant, user_from, message, *args, **kwargs):
    if settings.POPULATOR_MODE:
        return

    if not message:
        return

    data = {
        'user_from': user_from.uuid.__str__(),
        'message': message,
        'app_pk': applicant.pk
    }
    AddMessageToConversationTask().s(**data).apply_async()


def create_conversation_for_user_tagged(sender, instance, created, *args, **kwargs):
    if settings.POPULATOR_MODE:
        return
    if created:
        opportunity = instance.opportunity
        user = instance.user
        data = {
            'opportunity_id': opportunity.id,
            'user_from_id': user.id,
            'message': '',
            'files': [],
        }

        CreateOportunityConversationTask().s(**data).apply_async()

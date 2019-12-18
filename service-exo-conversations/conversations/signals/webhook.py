from django.conf import settings

from ..tasks import WebhookOpportunityFirstMessageTask


def new_message_opportunity_handler(sender, instance, *args, **kwargs):
    if settings.POPULATOR_MODE:
        return
    conversation = instance.conversation
    if conversation.is_opportunity_related:
        first_message = not conversation.messages.exclude(pk=instance.pk).exists()
        if first_message:
            WebhookOpportunityFirstMessageTask().s(
                pk=instance.pk).apply_async()

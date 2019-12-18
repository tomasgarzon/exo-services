from django.apps import apps
from django.conf import settings


def password_changed_handler(sender, instance, password, *args, **kwargs):
    Message = apps.get_model(
        app_label='exo_messages',
        model_name='Message')

    Message.objects.clear_messages(
        user=instance,
        code=settings.EXO_MESSAGES_CH_CODE_PENDING_PASSWORD,
    )

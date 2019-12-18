from django.apps import apps
from django.conf import settings


def email_address_handler(sender, **kwargs):
    Message = apps.get_model(
        app_label='exo_messages',
        model_name='Message')

    created = kwargs.get('created')
    instance = kwargs.get('instance')
    if created:
        if not instance.is_verified:
            Message.objects.create_message(
                user=instance.user,
                code=settings.EXO_MESSAGES_CH_CODE_PENDING_EMAIL,
                level=settings.EXO_MESSAGES_CH_ERROR,
                variables={
                    'email': instance.email,
                    'pk': instance.pk,
                    'verif_key': instance.verif_key,
                }
            )


def email_address_delete_handler(sender, **kwargs):
    Message = apps.get_model(
        app_label='exo_messages',
        model_name='Message')
    instance = kwargs.get('instance')

    Message.objects.clear_messages(
        user=instance.user,
        code=settings.EXO_MESSAGES_CH_CODE_PENDING_EMAIL,
    )


def verified_handler(sender, **kwargs):
    Message = apps.get_model(
        app_label='exo_messages',
        model_name='Message')
    instance = kwargs.get('instance')

    Message.objects.clear_messages(
        user=instance.user,
        code=settings.EXO_MESSAGES_CH_CODE_PENDING_EMAIL,
    )

    Message.objects.create_message(
        user=instance.user,
        code=settings.EXO_MESSAGES_CH_CODE_VALIDATED_EMAIL,
        level=settings.EXO_MESSAGES_CH_SUCCESS,
        can_be_closed=True,
        read_when_login=True,
        variables={
            'email': instance.email,
            'pk': instance.pk,
        }
    )

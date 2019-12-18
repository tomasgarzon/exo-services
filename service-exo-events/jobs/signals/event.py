from django.conf import settings

from ..models import Job


def post_save_event_handler(sender, instance, created, *args, **kwargs):
    for participant in instance.participants.all().filter_by_status(settings.EVENT_CH_ROLE_STATUS_ACTIVE):
        Job.objects.update_or_create(participant=participant)


def post_save_participant_handler(sender, instance, created, *args, **kwargs):
    if instance.is_active:
        Job.objects.update_or_create(participant=instance)
    elif hasattr(instance, 'job'):
        Job.objects.filter(participant=instance).delete()

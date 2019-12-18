from django.apps import apps
from django.db.models.signals import post_save, pre_delete

from .participant import post_save_participant
from .event import post_save_event, pre_delete_event


def setup_signals():
    Participant = apps.get_model(
        app_label='event',
        model_name='Participant')
    Event = apps.get_model(
        app_label='event',
        model_name='Event')

    post_save.connect(post_save_participant, sender=Participant)
    post_save.connect(post_save_event, sender=Event)
    pre_delete.connect(pre_delete_event, sender=Event)

from django.apps import apps
from django.db.models.signals import post_save, post_delete

from .event import (
    post_save_event_handler,
    post_save_participant_handler,
)

from .job import (
    post_job_save_handler,
    post_job_delete_handler,
)


def setup_signals():
    Job = apps.get_model('jobs', 'Job')
    Event = apps.get_model('event', 'Event')
    Participant = apps.get_model('event', 'Participant')

    post_save.connect(post_job_save_handler, sender=Job)
    post_delete.connect(post_job_delete_handler, sender=Job)

    post_save.connect(post_save_event_handler, sender=Event)
    post_save.connect(post_save_participant_handler, sender=Participant)

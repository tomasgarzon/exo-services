from django.apps import apps
from django.conf import settings
from django.shortcuts import get_object_or_404

from celery import Task

from utils.mails.handlers import mail_handler


class WorkshopReminderTask(Task):
    name = 'WorkshopReminderTask'
    ignore_result = True

    def run(self, pk, *args, **kwargs):
        Event = apps.get_model('event', 'Event')
        event = get_object_or_404(Event, pk=pk)

        mail_kwargs = {
            'workshop_name': event.title,
            'created_by': event.created_by_full_name,
        }
        mail_handler.send_mail(
            template='workshop_creation_reminder',
            recipients=settings.EVENT_CREATION_WORKSHOP_REMINDER_RECIPIENTS,
            **mail_kwargs)

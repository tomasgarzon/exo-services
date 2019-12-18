from datetime import datetime

from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from celery import Task

from auth_uuid.utils.user_wrapper import UserWrapper

from utils.mails.handlers import mail_handler

User = get_user_model()


class EventNotificationMixin:

    def get_managers_uuid(self):
        return User.objects.filter(
            user_permissions__codename=settings.EVENT_PERMS_MANAGE_EVENT,
        ).values_list('uuid', flat=True)

    def get_manager_user(self):
        manager_user_uuid = self.get_managers_uuid()[0]
        return User.objects.retrieve_remote_user_data_by_uuid(manager_user_uuid)

    def get_manager_recipients(self):
        managers_uuid = self.get_managers_uuid()
        return [
            User.objects.retrieve_remote_user_data_by_uuid(_).get('email')
            for _ in managers_uuid
        ]


class NotifyEventManagerTask(EventNotificationMixin, Task):
    name = 'NotifyEventManagerTask'
    ignore_result = True

    def run(self, pk, *args, **kwargs):
        Event = apps.get_model('event', 'Event')
        event = get_object_or_404(Event, pk=pk)
        mail_kwargs = {
            'event_title': event.title,
            'event_type_name': event.type_event_name,
            'event_date': datetime.strftime(event.start, '%d/%m/%Y'),
            'event_status': event.get__status_display(),
            'event_approved': event.is_approved,
            'public_url': '{}{}'.format(
                settings.EVENT_MANAGE_URL,
                event.uuid,
            ),
            'user_full_name': event.main_speaker_data.get('fullName'),
            'user_profile_url': event.main_speaker_data.get('profileUrl'),
        }
        mail_handler.send_mail(
            template='event_manager_notification',
            recipients=self.get_manager_recipients(),
            **mail_kwargs,
        )


class EventUpdatedOwnerNotificationTask(EventNotificationMixin, Task):
    name = 'NotifyEventOwnerTask'
    ignore_result = True

    def run(self, pk, *args, **kwargs):
        Event = apps.get_model('event', 'Event')
        event = get_object_or_404(Event, pk=pk)

        mail_kwargs = {
            'event_owner_short_name': event.main_speaker_data.get('shortName'),
            'event_title': event.title,
            'event_type_name': event.type_event_name,
            'event_date': datetime.strftime(event.start, '%d/%m/%Y'),
            'event_approved': event.is_approved,
            'reviewer_user_name': self.get_manager_user().get('fullName'),
            'comments': kwargs.get('comment', ''),
            'public_url': '{}{}'.format(
                settings.EVENT_DETAIL_URL,
                event.uuid,
            )
        }
        mail_handler.send_mail(
            template='event_owner_notification',
            recipients=[event.main_speaker_data.get('email')],
            bcc=self.get_manager_recipients(),
            **mail_kwargs,
        )


class SummitRequestTask(EventNotificationMixin, Task):
    name = 'SummitRequestTask'
    ignore_result = True

    def run(self, user_uuid, *args, **kwargs):
        user_wrapper = UserWrapper(uuid=user_uuid)
        mail_kwargs = {
            'user_full_name': user_wrapper.get_full_name(),
            'user_profile_url': user_wrapper.profile_url,
            'comments': kwargs.get('comment', ''),
        }
        mail_handler.send_mail(
            template='event_summit_notification',
            recipients=[settings.EVENT_SUMMIT_DISTRIBUTION_LIST_EMAIL],
            **mail_kwargs,
        )

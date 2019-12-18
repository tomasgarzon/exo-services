from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

from utils.descriptors import CustomFilterDescriptorMixin

from ..models.organizer import Organizer
from ..querysets import EventQuerySet
from ..tasks import NotifyEventManagerTask


class EventManagerMixin(CustomFilterDescriptorMixin):
    use_for_related_fields = True
    use_in_migrations = True
    queryset_class = EventQuerySet

    FILTER_DESCRIPTORS = [
        {
            'field': 'category',
            'options': settings.EVENT_TYPE_CHOICES,
        },
        {
            'field': 'status',
            'options': settings.EVENT_STATUS_CHOICES,
        },
    ]

    def get_queryset(self):
        return self.queryset_class(
            self.model,
            using=self._db,
        )

    def filter_by_category(self, category):
        return self.get_queryset().filter_by_category(category)

    def filter_by_status(self, status):
        return self.get_queryset().filter_by_status(status)

    def create_event(self, force_retrieve_user_data=True, **kwargs):
        organizers_data = kwargs.pop('organizers', [])
        participants_data = kwargs.pop('participants', [])
        user_from = kwargs.pop('user_from')
        user_data = {}

        if force_retrieve_user_data:
            _, user_data = get_user_model().objects.retrieve_remote_user_by_uuid(
                uuid=user_from.uuid,
                retrieve_response=True,
            )

        kwargs['created_by'] = user_from
        kwargs['created_by_full_name'] = user_data.get('fullName', '')
        instance = super().create(**kwargs)

        for organizer_data in organizers_data:
            organizer, _ = Organizer.objects.get_or_create(
                email=organizer_data.pop('email'),
                defaults=organizer_data,
            )
            instance.organizers.add(organizer)

        for participant_data in participants_data:
            instance.add_participant(**participant_data)

        if instance.is_openexo_workshop:
            instance.send_workshop_creation_reminder()

        NotifyEventManagerTask().s(pk=instance.pk).apply_async()

        return instance

    def filter_by_user(self, user):
        return self.get_queryset().filter_by_user(user)


class EventManager(EventManagerMixin, models.Manager):
    def get_queryset(self):
        return super().get_queryset().exclude(
            _status=settings.EVENT_CH_STATUS_DELETED,
        )


class AllPublicEventManager(EventManagerMixin, models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter_by_status(
            settings.EVENT_CH_STATUS_PUBLIC)


class AllEventManager(EventManagerMixin, models.Manager):

    def get_queryset(self):
        return super().get_queryset().all()

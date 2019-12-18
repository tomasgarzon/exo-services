import uuid

from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation

from django_extensions.db.fields import AutoSlugField
from model_utils.models import TimeStampedModel

from exo_role.models import ExORole
from utils.descriptors import ChoicesDescriptorMixin
from utils.models import CreatedByMixin
from utils.mixins import LocationTimezoneMixin

from ..conf import settings
from ..helpers import EventPermissionHelper
from ..managers.event import EventManager, AllPublicEventManager, AllEventManager
from ..models.participant import Participant
from ..models.organizer import Organizer
from ..tasks import WorkshopReminderTask, SyncParticipantTask


class Event(
        ChoicesDescriptorMixin,
        LocationTimezoneMixin,
        CreatedByMixin,
        TimeStampedModel):

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    organizers = models.ManyToManyField(
        'event.Organizer',
        blank=True,
        related_name='events',
    )

    title = models.CharField(max_length=255)
    sub_title = models.CharField(max_length=512, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    url_image = models.URLField(default='')

    slug = AutoSlugField(populate_from='title')

    _status = models.CharField(
        max_length=1,
        default=settings.EVENT_CH_STATUS_DEFAULT,
        choices=settings.EVENT_STATUS_CHOICES,
    )

    start = models.DateField(blank=True, null=True)
    end = models.DateField(blank=True, null=True)

    category = models.ForeignKey(
        'exo_role.Category',
        related_name='events',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    # deprectaed
    type_event = models.CharField(max_length=1)
    type_event_other = models.CharField(
        max_length=128,
        blank=True,
        null=True,
    )

    follow_type = models.CharField(
        max_length=1,
        default=settings.EVENT_CH_FOLLOW_MODE_DEFAULT,
        choices=settings.EVENT_FOLLOW_MODE_CHOICES,
    )

    url = models.CharField(
        max_length=512,
        blank=True,
        null=True,
    )

    languages = ArrayField(models.CharField(max_length=56), blank=True, null=True)

    show_price = models.BooleanField(default=False)
    amount = models.FloatField(null=True, default=0)
    currency = models.CharField(
        max_length=1,
        default=settings.EVENT_CH_CURRENCY_DEFAULT,
        choices=settings.EVENT_CURRENCY_CHOICES,
    )
    credentials = GenericRelation(
        'certification.CertificationGroup',
        related_query_name='events')

    CHOICES_DESCRIPTOR_FIELDS = [
        '_status',
    ]
    CHOICES_DESCRIPTOR_FIELDS_CHOICES = [
        settings.EVENT_STATUS_CHOICES,
    ]

    all_objects = AllEventManager()
    objects = EventManager()
    public_objects = AllPublicEventManager()

    class Meta:
        verbose_name = 'Event'
        verbose_name_plural = 'Events'
        ordering = ['-start']
        permissions = settings.EVENT_ALL_PERMISSIONS

    def __str__(self):
        return '{} - {}'.format(
            self.type_event_name,
            self.title,
        )

    @property
    def status(self):
        return self._status

    @property
    def is_approved(self):
        return self._status == settings.EVENT_CH_STATUS_PUBLIC

    @status.setter
    def status(self, user_status):
        try:
            user, new_status = user_status
            assert type(new_status) == str
        except AssertionError:
            raise AssertionError('Status not valid')
        except ValueError:
            raise ValueError('User or new status missed')

        try:
            permission_helper = EventPermissionHelper()
            if new_status in [settings.EVENT_CH_STATUS_PUBLIC, settings.EVENT_CH_STATUS_UNDER_REVIEW]:
                assert permission_helper.can_publish_event(user)
            else:
                assert permission_helper.can_edit_event(user, self)
        except AssertionError:
            raise AssertionError('User has not permission to perform this action')

        self._status = new_status
        self.save(update_fields=['_status'])

    @property
    def type_event_name(self):
        real_type_event_name = dict(settings.EVENT_TYPE_CHOICES).get(self.category.code)
        if self.category.code == settings.EXO_ROLE_CATEGORY_OTHER:
            real_type_event_name = self.type_event_other

        return real_type_event_name

    @property
    def event_image(self):
        image_url = self.url_image
        if not image_url:
            image_url = self.main_speaker_data.get('profilePicture')
        return image_url

    @property
    def speaker_role(self):
        return list(filter(
            lambda x: x[1] == settings.EVENT_SPEAKER_NAME,
            settings.EVENT_PARTICIPANT_ROLE_CHOICES.get(self.category.code)
        ))[0][0]

    @property
    def main_speaker(self):
        return self.speakers.filter(order=0).first()

    @property
    def main_speaker_data(self):
        _, user_data = get_user_model().objects.retrieve_remote_user_by_uuid(
            uuid=self.main_speaker.user.uuid,
            retrieve_response=True,
        )
        user_data['profileUrl'] = '{}{}'.format(
            settings.DOMAIN_NAME,
            user_data.get('profileUrl')
        )
        user_data['profilePicture'] = [value for key, value in user_data.get('profilePicture') if key[0] == 48][0]
        return user_data

    @property
    def price(self):
        price = 'Free'
        amount = self.amount
        currency = self.get_currency_display()

        if self.amount:
            price_mask = getattr(settings, 'EVENT_PRICE_STR_{}'.format(self.currency))
            price = price_mask % locals()

        return price if self.show_price else None

    @property
    def is_openexo_talk(self):
        return self.category.code == settings.EXO_ROLE_CATEGORY_TALK

    @property
    def is_openexo_workshop(self):
        return self.category.code == settings.EXO_ROLE_CATEGORY_WORKSHOP

    @property
    def is_openexo_summit(self):
        return self.category.code == settings.EXO_ROLE_CATEGORY_SUMMIT

    @property
    def is_other(self):
        return self.category.code == settings.EXO_ROLE_CATEGORY_OTHER

    def publish_event(self, user):
        self.status = user, settings.EVENT_CH_STATUS_PUBLIC

    def update_organizers(self, organizers_data):
        self.organizers.clear()
        for organizer_data in organizers_data:
            organizer_email = organizer_data.pop('email')
            organizer, created = Organizer.objects.get_or_create(
                email=organizer_email,
            )
            if not created:
                Organizer.objects.filter(
                    email=organizer_email
                ).update(**organizer_data)
            self.organizers.add(organizer)

    def update_participants(self, participants_data):
        posted_participants = [
            _.get('user', {}).get('uuid') for _ in participants_data
            if 'user' in _
        ]

        self.participants.exclude(
            user__uuid__in=posted_participants
        ).update(status=settings.EVENT_CH_ROLE_STATUS_DELETED)
        self.participants.filter(
            user__uuid__in=posted_participants,
            status=settings.EVENT_CH_ROLE_STATUS_DELETED,
        ).update(status=settings.EVENT_CH_ROLE_STATUS_ACTIVE)

        existing_participants = self.participants.values_list(
            'user__uuid',
            flat=True,
        )

        for participant_data in participants_data:
            user_uuid = participant_data.pop('user').get('uuid')
            if user_uuid not in existing_participants:
                participant_data['uuid'] = user_uuid
                self.add_participant(**participant_data)
            else:
                self.participants.filter(
                    user__uuid=user_uuid,
                ).update(order=participant_data.get('order'))

    def add_participant(self, exo_role, *args, **kwargs):
        user_uuid = kwargs.pop('uuid', kwargs.pop('user', {}).get('uuid', None))
        if user_uuid and self.participants.filter(user__uuid=user_uuid).exists():
            return self.participants.filter(user__uuid=user_uuid).first()

        if user_uuid:
            user, remote_data = get_user_model(
            ).objects.retrieve_remote_user_by_uuid(
                user_uuid,
                retrieve_response=True,
            )
            full_name = remote_data.get('fullName')
            email = remote_data.get('email')

        else:
            user = get_user_model().objects.create(
                uuid=uuid.uuid4())
            full_name = kwargs.get('full_name')
            email = kwargs.get('user_email')
        user_data = {
            'user_name': full_name,
            'user_email': email
        }
        order = kwargs.pop('order', self.participants.count())
        participant, _ = Participant.objects.get_or_create(
            user=user,
            event=self,
            exo_role=exo_role,
            order=order,
            **user_data
        )
        return participant

    def add_participant_public(self, name, email, *args, **kwargs):
        if self.participants.filter_by_email(email).exists():
            participant = self.participants.filter_by_email(email).first()
        else:
            exo_role_code = Participant.get_role_by_name(
                settings.EVENT_PARTICIPANT_NAME,
                self.category.code,
            )
            participant = Participant.objects.create(
                event=self,
                user_name=name,
                user_email=email,
                exo_role=ExORole.objects.get(code=exo_role_code),
                order=self.participants.count(),
            )

            SyncParticipantTask().s(
                name=participant.user_name,
                email=participant.user_email,
                entry_point=settings.EVENT_SUMMITS_SIGNUPS_ENTRY_POINT,
            ).apply_async()

        return participant

    @property
    def location_for_certification(self):
        is_on_site = settings.EVENT_CH_FOLLOW_MODE_ON_SITE == self.follow_type
        if is_on_site and self.location:
            return self.location
        else:
            return self.get_follow_type_display()

    @property
    def description_for_certification(self):
        description = self.type_event_name
        if self.description:
            description = self.description
        else:
            description = self.title
            if self.sub_title:
                description += ', {}'.format(self.sub_title)
        return description

    @property
    def speakers(self):
        return self.participants.filter(exo_role__code=self.speaker_role)

    def send_workshop_creation_reminder(self):
        if not settings.POPULATOR_MODE:
            WorkshopReminderTask().s(pk=self.pk).apply_async()

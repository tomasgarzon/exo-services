from django.conf import settings
from django.db import models
from django.contrib.contenttypes.fields import GenericRelation

from itertools import chain
from model_utils.models import TimeStampedModel

from utils.descriptors import ChoicesDescriptorMixin
from utils.models import CreatedByMixin

from ..managers.participant import ParticipantManager


class Participant(
        ChoicesDescriptorMixin,
        CreatedByMixin,
        TimeStampedModel):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='events',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    user_name = models.CharField(
        verbose_name='User name',
        max_length=255,
    )
    user_email = models.EmailField(
        verbose_name='User email',
        max_length=255,
    )

    order = models.IntegerField(default=0)

    event = models.ForeignKey(
        'event.Event',
        related_name='participants',
        on_delete=models.CASCADE,
    )

    # deprecated
    role = models.CharField(max_length=3)
    exo_role = models.ForeignKey(
        'exo_role.ExORole',
        related_name='event_participants',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=1,
        default=settings.EVENT_CH_ROLE_STATUS_DEFAULT,
        choices=settings.EVENT_ROLE_STATUS_CHOICES,
    )

    certifications = GenericRelation(
        'certification.CertificationCredential',
        related_query_name='participants',
    )

    CHOICES_DESCRIPTOR_FIELDS = [
        'status',
    ]
    CHOICES_DESCRIPTOR_FIELDS_CHOICES = [
        settings.EVENT_ROLE_STATUS_CHOICES,
    ]

    objects = ParticipantManager()

    class Meta:
        verbose_name = 'Participant'
        verbose_name_plural = 'Participants'

    def __str__(self):
        return '{} {} {}'.format(
            self.user_email,
            self.event.title,
            self.get_status_display(),
        )

    @property
    def category(self):
        return self.event.category

    @classmethod
    def get_role_by_name(cls, role_name, category_code=None):
        roles = list(map(lambda x: x[0], filter(
            lambda x: x[1] == role_name,
            list(chain.from_iterable([_[1] for _ in settings.EVENT_PARTICIPANT_ROLE_CHOICES.items()]))
        )))
        if category_code:
            try:
                roles = list(filter(
                    lambda x: x in dict(settings.EVENT_PARTICIPANT_ROLE_CHOICES.get(category_code, {})).keys(),
                    roles,
                ))[0]
            except IndexError:
                roles = []

        return roles

    @property
    def participant_role_name(self):
        return dict(
            settings.EVENT_PARTICIPANT_ROLE_CHOICES.get(self.event.category.code)
        ).get(self.exo_role.code)

    @property
    def is_speaker(self):
        return self.participant_role_name == settings.EVENT_SPEAKER_NAME

    @property
    def is_participant(self):
        return self.participant_role_name == settings.EVENT_PARTICIPANT_NAME

    @property
    def is_trainer(self):
        return self.participant_role_name == settings.EVENT_TRAINER_NAME

    @property
    def is_collaborator(self):
        return self.participant_role_name == settings.EVENT_COLLABORATOR_NAME

    @property
    def is_facilitator(self):
        return self.participant_role_name == settings.EVENT_FACILITATOR_NAME

    @property
    def is_organizer(self):
        return self.participant_role_name == settings.EVENT_ORGANIZER_NAME

    @property
    def is_coach(self):
        return self.participant_role_name == settings.EVENT_COACH_NAME

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from model_utils.models import TimeStampedModel

from utils.descriptors import ChoicesDescriptorMixin

from ..manager import ValidationManager
from ..conf import settings


class Validation(ChoicesDescriptorMixin, TimeStampedModel):
    project = models.ForeignKey(
        'project.Project',
        related_name='validations',
        on_delete=models.CASCADE
    )
    validation_type = models.CharField(
        choices=settings.VALIDATION_CH_TYPE,
        default=settings.VALIDATION_CH_WARNING,
        max_length=1,
    )
    status = models.CharField(
        choices=settings.VALIDATION_CH_STATUS,
        default=settings.VALIDATION_CH_PENDING,
        max_length=1,
    )
    validation_detail = models.CharField(
        max_length=2,
        blank=True, null=True,
        choices=settings.VALIDATION_CH_DETAIL,
    )
    subject = models.CharField(
        max_length=100,
    )
    message = models.TextField(blank=True, null=True)
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=True,
    )
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    objects = ValidationManager()

    CHOICES_DESCRIPTOR_FIELDS = [
        'status', 'validation_type', 'validation_detail',
    ]

    class Meta:
        verbose_name = 'Validation'

    def __str__(self):
        return '{} - {}'.format(self.project, self.subject)

    @property
    def is_pending(self):
        return self.status == settings.VALIDATION_CH_PENDING

    @property
    def is_fixed(self):
        return self.status == settings.VALIDATION_CH_FIXED

    @property
    def is_warning(self):
        return self.validation_type == settings.VALIDATION_CH_WARNING

    @property
    def is_error(self):
        return self.validation_type == settings.VALIDATION_CH_ERROR

    def pending(self):
        self.status = settings.VALIDATION_CH_PENDING
        self.save(update_fields=['status', 'modified'])

    def fixed(self):
        self.status = settings.VALIDATION_CH_FIXED
        self.save(update_fields=['status', 'modified'])

    def fix_url(self):  # noqa
        if self.validation_detail == settings.VALIDATION_CH_NO_ZOOM:
            return reverse(
                'admin:zoom_project_zoomsettings_change',
                args=[self.object_id],
            )

        elif self.validation_detail == settings.VALIDATION_CH_NO_SURVEY:
            return reverse(
                'project:project:team:edit', args=[
                    self.project.pk,
                    self.object_id,
                ],
            )

        elif self.validation_detail == settings.VALIDATION_CH_NO_MANAGER:
            return reverse('project:project:consultants', args=[self.project.pk])

        elif self.validation_detail == settings.VALIDATION_CH_ASSIGNMENT_NO_DAY:
            return reverse(
                'project:project:assignment:edit', args=[
                    self.project.pk,
                    self.object_id,
                ],
            )

        elif self.validation_detail == settings.VALIDATION_CH_ASSIGNMENT_PRIVATE:
            return reverse('project:project:assignment:list', args=[self.project.pk])

        elif self.validation_detail == settings.VALIDATION_CH_NO_TEAM:
            return reverse('project:project:team:list', args=[self.project.pk])

        elif self.validation_detail == settings.VALIDATION_CH_PART_PASS:
            return reverse('project:project:settings', args=[self.project.pk])

        elif self.validation_detail in [
                settings.VALIDATION_CH_NO_START,
                settings.VALIDATION_CH_NO_CITY,
                settings.VALIDATION_CH_NO_AGENDA,
        ]:
            return reverse('project:project:dashboard', args=[self.project.pk])

        elif self.validation_detail in [
                settings.VALIDATION_CH_PERIOD_1_NO_START_DATE,
                settings.VALIDATION_CH_SPRINT_AUTOMATED_MICROLEARNINGS,
                settings.VALIDATION_CH_SPRINT_AUTOMATED_FEEDBACKS,
        ]:
            return reverse('project:project:steps', args=[self.project.pk])

        return ''

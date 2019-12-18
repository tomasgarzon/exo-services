from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

from model_utils.models import TimeStampedModel
from typeform_feedback.models import GenericTypeformFeedback

from ..managers.step_stream import StepStreamManager


class StepStream(TimeStampedModel):
    step = models.ForeignKey(
        'Step', related_name='streams',
        on_delete=models.CASCADE)
    stream = models.CharField(
        verbose_name='Stream',
        max_length=1,
        choices=settings.PROJECT_STREAM_CH_TYPE,
        default=settings.PROJECT_STREAM_CH_TYPE_DEFAULT,
    )
    goal = models.CharField(
        verbose_name='Goal',
        max_length=200,
        null=True, blank=True,
    )
    guidelines = models.TextField(blank=True, null=True, default='')
    typeform_feedback = GenericRelation(
        'typeform_feedback.GenericTypeformFeedback',
        related_query_name='related_to',
    )

    CHOICES_DESCRIPTOR_FIELDS = ['stream']

    objects = StepStreamManager()

    def __str__(self):
        return '{} {}'.format(self.step, self.get_stream_display())

    def _create_typeform_feedback(self):
        ct = ContentType.objects.get_for_model(self)
        return GenericTypeformFeedback.objects.create(
            object_id=self.pk,
            content_type=ct,
            typeform_type=settings.TYPEFORM_FEEDBACK_CH_WEEKLY,
        )

    def get_or_create_typeform_feedback(self):
        try:
            return self.typeform_feedback.all()[0], False
        except IndexError:
            return self._create_typeform_feedback(), True

    @property
    def exists_typeform_feedback(self):
        return self.typeform_feedback.exists()

    @property
    def project(self):
        return self.step.project

    @property
    def is_guidelines_filled(self):
        return self.guidelines

    def has_microlearning(self):
        return hasattr(self, 'microlearning')

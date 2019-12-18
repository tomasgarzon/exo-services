from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType

from model_utils.models import TimeStampedModel
from typeform_feedback.models import GenericTypeformFeedback

from ..managers.step_stream import StepStreamManager


class StepStream(TimeStampedModel):
    step = models.ForeignKey(
        'Step',
        related_name='streams',
        on_delete=models.CASCADE)
    stream = models.ForeignKey(
        'utils.Stream',
        on_delete=models.CASCADE,
        related_name='step_streams',
        blank=True, null=True)
    goal = models.CharField(
        max_length=200,
        null=True, blank=True)
    typeform_feedback = GenericRelation(
        'typeform_feedback.GenericTypeformFeedback',
        related_query_name='related_to',
    )

    objects = StepStreamManager()

    def __str__(self):
        return '{}-{}'.format(self.step, self.stream)

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

    def has_microlearning(self):
        return hasattr(self, 'microlearning')

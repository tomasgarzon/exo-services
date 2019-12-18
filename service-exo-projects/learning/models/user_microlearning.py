from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import JSONField

from model_utils.models import TimeStampedModel

from utils.descriptors import ChoicesDescriptorMixin

from ..managers.user_micro_learning import UserMicroLearningManager
from ..signals_define import microlearning_webhook_received_send


class UserMicroLearning(ChoicesDescriptorMixin, TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=False,
        on_delete=models.CASCADE,
        related_name='microlearnings',
    )
    microlearning = models.ForeignKey(
        'MicroLearning',
        null=False, blank=False,
        related_name='responses',
        on_delete=models.CASCADE,
    )
    team = models.ForeignKey(
        'team.Team',
        null=True,
        on_delete=models.CASCADE,
        related_name='microlearnings_responses'
    )
    responses = JSONField(blank=True, null=True, default=dict)
    status = models.CharField(
        max_length=1,
        blank=False, null=False,
        choices=settings.LEARNING_USER_MICROLEARNING_STATUS_CHOICES,
        default=settings.LEARNING_USER_MICROLEARNING_STATUS_PENDING,
    )
    score = models.IntegerField(blank=True, null=True)
    objects = UserMicroLearningManager()

    class Meta:
        unique_together = [('user', 'microlearning', 'team')]

    def __str__(self):
        return '{} - {}-{}'.format(self.user, self.microlearning, self.get_status_display())

    @property
    def project(self):
        return self.microlearning.project

    @property
    def typeform_url(self):
        return '{}?{}={}'.format(
            self.microlearning.typeform_url,
            settings.LEARNING_USER_MICROLEARNING_TYPEFORM_PARAM,
            self.pk)

    def add_typeform_response(self, score, response):
        if self.responses == {}:
            self.responses = []
        self.responses.append(response)
        self.status = settings.LEARNING_USER_MICROLEARNING_STATUS_DONE
        self.score = score
        self.save(update_fields=['responses', 'status', 'modified', 'score'])
        microlearning_webhook_received_send.send(
            sender=self.__class__,
            user_microlearning=self,
        )

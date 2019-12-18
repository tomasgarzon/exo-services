from django.db import models
from model_utils.models import TimeStampedModel

from utils.descriptors import ChoicesDescriptorMixin

from .conf import settings


class ExOHub(ChoicesDescriptorMixin, TimeStampedModel):
    name = models.CharField(max_length=100)
    _type = models.CharField(
        max_length=1,
        choices=settings.EXO_HUB_CH_EXO_TYPE,
    )
    order = models.IntegerField()
    _users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='_hubs',
        through='relation.HubUser',
    )

    CHOICES_DESCRIPTOR_FIELDS = ['_type']

    class Meta:
        verbose_name = 'ExOHub'
        verbose_name_plural = 'ExOHubs'
        ordering = ['order']

    def __str__(self):
        return self.name

    def get_circle_name(self):
        return dict(settings.EXO_HUB_CIRCLES_NAMES).get(self._type, self.name)

from django.db import models

from model_utils.models import TimeStampedModel

from utils.models import CreatedByMixin


class Organizer(CreatedByMixin, TimeStampedModel):

    uuid = models.UUIDField(
        editable=False,
        unique=True,
        blank=True,
        null=True,
    )
    name = models.CharField(max_length=255)
    email = models.EmailField(
        verbose_name='Organizer Email',
        max_length=255,
        unique=True,
    )
    url = models.CharField(max_length=255)

    logo = models.ImageField(
        verbose_name='Logo',
        upload_to='logos',
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = 'Organizer'
        verbose_name_plural = 'Organizers'

    def __str__(self):
        return self.name if not self.uuid else self.uuid

    def get_letter_initial(self):
        return self.name[:2].upper()

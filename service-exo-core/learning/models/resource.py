from django.db import models

from model_utils.models import TimeStampedModel

from utils.models import CreatedByMixin, UniqueOrderMixin

from ..managers.resource import ResourceManager
from ..conf import settings


# Create your models here.
class Resource(CreatedByMixin, UniqueOrderMixin, TimeStampedModel):
    name = models.CharField(max_length=150)
    description = models.CharField(max_length=200, blank=True, null=True)
    order = models.IntegerField()
    file = models.FileField(upload_to='resources', blank=True, null=True)
    link = models.CharField(max_length=200, blank=True, null=True)
    active = models.BooleanField(default=True)
    tags = models.ManyToManyField(
        'Tag',
        verbose_name='Tags',
    )

    objects = ResourceManager()

    class Meta:
        verbose_name = 'Resource'
        verbose_name_plural = 'Resources'
        ordering = ['order']
        permissions = settings.LEARNING_ALL_RESOURCE_PERMS

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.order:
            self.order = self.create_unique(
                'order',
                active=True,
            )
        super(Resource, self).save(*args, **kwargs)  # Call the "real" save() method.

    @property
    def is_file(self):
        return bool(self.file)

    def get_download_url(self):
        if self.file:
            return self.file.url
        return self.link

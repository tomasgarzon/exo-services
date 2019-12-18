from django.db import models
from django.utils.dateparse import parse_datetime
from django.urls import reverse

from model_utils.models import TimeStampedModel
from multiselectfield import MultiSelectField

from ..managers.resource import ResourceManager
from ..conf import settings
from .mixins import VideoResourceMixin


class Resource(VideoResourceMixin, TimeStampedModel):
    type = models.CharField(
        max_length=1,
        choices=settings.RESOURCE_CH_TYPES,
        default=settings.RESOURCE_CH_TYPE_VIDEO_VIMEO)
    status = models.CharField(
        max_length=1,
        choices=settings.RESOURCE_CH_STATUS,
        default=settings.RESOURCE_CH_STATUS_DRAFT)
    name = models.CharField(
        blank=False, null=False, max_length=555)
    description = models.TextField(
        blank=True, null=True)
    link = models.URLField(
        blank=True, null=True)
    url = models.URLField(
        blank=True, null=True)
    thumbnail = models.URLField(
        blank=True, null=True)
    duration = models.IntegerField(
        blank=True, null=True)
    tags = models.ManyToManyField(
        'Tag', blank=True)
    sections = MultiSelectField(
        choices=settings.RESOURCE_CH_SECTIONS,
        blank=True, null=True)
    projects = models.TextField(
        blank=True,
        null=True,
        default='')
    extra_data = models.TextField(
        blank=True,
        null=True)

    objects = ResourceManager()

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def is_draft(self):
        return self.status == settings.RESOURCE_CH_STATUS_DRAFT

    @property
    def is_type_filestack(self):
        return self.type == settings.RESOURCE_CH_TYPE_FILESTACK

    def get_handle(self):
        return self.link.split(settings.RESOURCE_FILESTACK_CDN_URL)[1][1:]

    @property
    def url_hash(self):
        url = None

        if self.is_type_filestack:
            handle = self.get_handle()
            url = reverse('resource:resource-redirect',
                          kwargs={'handle': handle,
                                  'filename': self.extra_data.get('filename', None)})
        return url

    def has_modifications(self, modified_time):
        return self.modified_time < parse_datetime(modified_time)

    @classmethod
    def get_provider_status(cls, status):
        try:
            status = settings.RESOURCE_PROVIDERS_STATUS[status]
        except KeyError:
            status = settings.RESOURCE_CH_STATUS_DRAFT

        return status

    def set_as_available(self, websocket=True):
        self.status = settings.RESOURCE_CH_STATUS_AVAILABLE
        self.save(update_fields=['status'])
        if websocket:
            self.notificate_update_websocket()

    def set_as_error(self, websocket=True):
        self.status = settings.RESOURCE_CH_STATUS_ERROR
        self.save(update_fields=['status'])
        if websocket:
            self.notificate_update_websocket()

    def delete(self, *args, **kwargs):
        self.status = settings.RESOURCE_CH_STATUS_REMOVED
        self.save(update_fields=['status'])

    def force_delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

    @property
    def project_list(self):
        return self.projects.split(',') if self.projects is not None else []

    @project_list.setter
    def project_list(self, value):
        if value is None:
            self.projects = ''
        else:
            project_list = self.project_list
            project_list.append(str(value))
            self.projects = ','.join(project_list)
        self.save(update_fields=['projects'])

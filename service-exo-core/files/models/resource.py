import tagulous

from django.db import models
from django.urls import reverse
from django.contrib.postgres.fields import JSONField

from autoslug import AutoSlugField
from sizefield.models import FileSizeField

from model_utils.models import TimeStampedModel
from utils.models import UniqueNameMixin
from utils.signal_receivers import get_subclasses
from utils.tags import PublicTag

from ..conf import settings
from ..storage import ResourceStorage
from ..managers.resource import ResourceManager


class Resource(UniqueNameMixin, TimeStampedModel):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.CASCADE,
        null=True, blank=True,
    )
    name = models.CharField(
        'Name',
        max_length=100,
    )
    description = models.TextField('Description', blank=True, null=True)
    slug = AutoSlugField(
        populate_from='name',
        always_update=True,
        max_length=200,
    )
    extension = models.CharField(
        max_length=10,
        blank=True,
        null=True,
    )
    mimetype = models.CharField(
        max_length=150,
        blank=True,
        null=True,
    )
    # private name, without extension
    _filename = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )
    link = models.CharField(max_length=200, blank=True, null=True)
    metadata = JSONField(blank=True, null=True)
    tags = tagulous.models.TagField(
        force_lowercase=True,
        tree=True,
    )
    file_size = FileSizeField(blank=True, null=True)
    objects = ResourceManager()

    class Meta:
        verbose_name = 'Resource'
        verbose_name_plural = 'Resources'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = self.create_unique(
            self.name,
            'name',
            suffix=' (%s)',
        )
        if not self.id:
            tag_original = [kwargs.pop('tag_original', settings.FILES_GENERAL_TAG)]
            self.tags = tag_original
        super(Resource, self).save(*args, **kwargs)  # Call the "real" save() method.

    @property
    def is_link(self):
        return self.link is not None

    @property
    def is_file(self):
        return self._filename is not None

    @property
    def type(self):
        if self.is_link:
            return settings.FILES_TYPE_LINK
        return settings.FILES_MIMETYPE.get(
            self.mimetype,
            settings.FILES_MIMETYPE.get('default'),
        )

    @property
    def url(self):
        if self.is_link:
            return self.link
        else:
            return self.get_url()

    def get_url(self):
        return reverse(
            'files:download', kwargs={
                'slug': self.file_name,
            },
        )

    def read(self):
        storage = ResourceStorage()
        return storage.open(self._filename).read()

    def hydrate_project(self, project):
        self._project = project

    @property
    def file_name(self):
        return '{}.{}'.format(self.slug, self.extension)

    @property
    def public_tags(self):
        project = self._project
        assert project
        classes_list = get_subclasses(PublicTag)
        classes_list.pop(0)
        tags = []
        for class_obj in classes_list:
            queryset = class_obj.objects.filter_by_project(project)
            for instance in queryset:
                if instance.slug in self.tags.all():
                    tags.extend(instance.public_tags)
        seen = set()
        seen_add = seen.add
        return [x for x in tags if not (x in seen or seen_add(x))]  # remove duplicates

    @property
    def is_general(self):
        return settings.FILES_GENERAL_TAG in self.tags

    @property
    def is_user(self):
        return settings.FILES_USER_TAG in self.tags

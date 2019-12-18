from django.db import models
from django.conf import settings
import reversion

from ..queryset.team import TeamQuerySet


class TeamManager(models.Manager):
    use_for_related_fields = True
    queryset_class = TeamQuerySet

    def get_queryset(self):
        return self.queryset_class(self.model, using=self._db)

    def filter_by_project(self, project):
        return self.get_queryset().filter_by_project(project)

    def filter_by_stream(self, stream):
        return self.get_queryset().filter_by_stream(stream)

    def filter_by_stream_edge(self):
        return self.get_queryset().filter_by_stream_edge()

    def filter_by_stream_core(self):
        return self.get_queryset().filter_by_stream_core()

    def create(self, *args, **kwargs):
        if 'image' not in kwargs and kwargs.get('stream') is not None:
            stream_code = kwargs.get('stream').code
            current = self.get_queryset().filter_by_project(
                kwargs.get('project')).filter_by_stream(stream_code).count()
            images_by_stream = settings.TEAM_IMAGES.get(stream_code, [])
            position = current % 3
            image = images_by_stream[position]
            kwargs['image'] = image
        with reversion.create_revision():
            new_object = super().create(*args, **kwargs)
            reversion.set_user(kwargs.get('created_by'))
            reversion.set_comment("Created")
            return new_object

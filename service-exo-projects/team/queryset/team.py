from django.db import models

from ..conf import settings


class TeamQuerySet(models.QuerySet):

    def filter_by_project(self, project):
        return self.filter(project=project)

    def filter_by_stream(self, stream):
        return self.filter(stream__code=stream)

    def filter_by_stream_edge(self):
        return self.filter_by_stream(settings.UTILS_STREAM_CH_EDGE)

    def filter_by_stream_core(self):
        return self.filter_by_stream(settings.UTILS_STREAM_CH_CORE)

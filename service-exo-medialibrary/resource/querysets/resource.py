from django.db import models
from django.db.models import Q

from ..conf import settings


class ResourceQueryset(models.QuerySet):

    def filter_by_url(self, url):
        return self.filter(url=url)

    def filter_by_tags(self, tags):
        return self.filter(tags__in=tags)

    def filter_by_status(self, status):
        is_status_list = type(status) == list
        my_filter = Q(status__in=status) if is_status_list else Q(status=status)
        return self.filter(my_filter).distinct()

    def filter_by_type(self, type_resource):
        return self.filter(type=type_resource)

    def filter_by_section(self, section):
        return self.filter(Q(sections__contains=section))

    def filter_by_uuid(self, uuid):
        return self.filter(projects__contains=[uuid])

    def drive(self):
        return self.filter_by_type(settings.RESOURCE_CH_TYPE_VIDEO_DRIVE)

    def dropbox(self):
        return self.filter_by_type(settings.RESOURCE_CH_TYPE_VIDEO_DROPBOX)

    def available(self):
        return self.filter_by_status(settings.RESOURCE_CH_STATUS_AVAILABLE)

    def draft(self):
        return self.filter_by_status(settings.RESOURCE_CH_STATUS_DRAFT)

    def removed(self):
        return self.filter_by_status(settings.RESOURCE_CH_STATUS_REMOVED)

    def error(self):
        return self.filter_by_status(settings.RESOURCE_CH_STATUS_ERROR)

    def draft_and_available(self):
        status = [
            settings.RESOURCE_CH_STATUS_DRAFT,
            settings.RESOURCE_CH_STATUS_AVAILABLE
        ]
        return self.filter_by_status(status)

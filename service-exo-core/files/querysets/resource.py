from django.db.models import QuerySet
from django.core.exceptions import ValidationError


class ResourceQuerySet(QuerySet):

    def filter_by_project(self, project):
        return self.filter(tags=project.slug)

    def filter_by_object(self, generic_object):
        if not hasattr(generic_object, 'slug'):
            raise ValidationError('Object required to have slug field')
        return self.filter(tags=generic_object.slug)

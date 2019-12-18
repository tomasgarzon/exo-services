from django.db import models
from django.conf import settings

from ..querysets.resource import ResourceQuerySet


class ResourceManager(models.Manager):
    queryset_class = ResourceQuerySet

    def get_queryset(self):
        return self.queryset_class(self.model, using=self._db)

    def filter_by_project(self, project):
        return self.get_queryset().filter_by_project(project)

    def filter_by_assignment(self, assignment):
        return self.get_queryset().filter_by_object(assignment)

    def create_resource(
            self, user_from, root_name, name, extension, content_type, *args, **kwargs
    ):
        new_node = self.create(
            created_by=user_from,
            name=name,
            extension=extension,
            mimetype=content_type,
            _filename=root_name,
            link=kwargs.get('link'),
            description=kwargs.get('description'),
            file_size=kwargs.get('file_size', None),
        )

        return new_node

    def create_user_resource(self, user_from, team, related, **kwargs):
        new_resource = self.model(
            created_by=user_from,
            **kwargs
        )
        new_resource.save(tag_original=settings.FILES_USER_TAG)
        related.add_user_resource(user_from, team, new_resource)
        return new_resource

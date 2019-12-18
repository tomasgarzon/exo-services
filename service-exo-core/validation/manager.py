from django.db import models

from utils.descriptors import CustomFilterDescriptorMixin

from .conf import settings
from .queryset import ValidationQuerySet


class ValidationManager(CustomFilterDescriptorMixin, models.Manager):
    use_for_related_fields = True
    use_in_migrations = True
    queryset_class = ValidationQuerySet
    FILTER_DESCRIPTORS = [
        {
            'field': 'status',
            'options': settings.VALIDATION_CH_STATUS,
        }, {
            'field': 'validation_type',
            'options': settings.VALIDATION_CH_TYPE,
        }, {
            'field': 'validation_detail',
            'options': settings.VALIDATION_CH_DETAIL,
        },
    ]

    def get_queryset(self):
        return self.queryset_class(self.model, using=self._db)

    def filter_by_status(self, status):
        return self.get_queryset().filter_by_status(status)

    def filter_by_validation_type(self, type_value):
        return self.get_queryset().filter_by_validation_type(type_value)

    def filter_by_validation_detail(self, detail):
        return self.get_queryset().filter_by_validation_detail(detail)

    def create_warning(self, project, detail, message='', content_type=None):
        return self.create(
            project=project,
            validation_type=settings.VALIDATION_CH_WARNING,
            validation_detail=detail,
            subject=settings.VALIDATION_LABEL_VALIDATION[detail],
            message=message,
            content_type=content_type,
        )

    def create_error(self, project, detail, message='', content_type=None):
        return self.create(
            project=project,
            validation_type=settings.VALIDATION_CH_ERROR,
            validation_detail=detail,
            subject=settings.VALIDATION_LABEL_VALIDATION[detail],
            message=message,
            content_type=content_type,
        )

    def clear_validations(self, project):
        project.validations.all().delete()

    def filter_by_project(self, project):
        return self.get_queryset().filter_by_project(project)

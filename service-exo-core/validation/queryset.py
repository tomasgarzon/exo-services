from django.db.models import Q

from utils.queryset import QuerySetFilterComplexMixin
from utils.descriptors import CustomFilterDescriptorMixin

from .conf import settings


class ValidationQuerySet(CustomFilterDescriptorMixin, QuerySetFilterComplexMixin):
    _fields_from_form = {
        'search': [
            'subject__icontains',
        ],
    }
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

    def filter_by_status(self, status):
        if type(status) == list:
            q_filter = Q(status__in=status)
        else:
            q_filter = Q(status=status)

        return self.filter(q_filter).distinct()

    def filter_by_validation_type(self, type_value):
        return self.filter(validation_type=type_value)

    def filter_by_validation_detail(self, detail):
        return self.filter(validation_detail=detail)

    def filter_by_project(self, project):
        return self.filter(project=project)

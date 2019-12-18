from django.db.models import Q
from django.contrib.auth import get_user_model

from utils.queryset import QuerySetFilterComplexMixin
from registration.models import RegistrationProcess

from ..conf import settings


class ConsultantQuerySet(QuerySetFilterComplexMixin):
    _fields_from_form = {
        'search': [
            'user__short_name__icontains',
            'user__full_name__icontains',
            'user__location__icontains',
            'user__consultant__languages__name__icontains',
        ],
        'name': ['user__short_name__icontains', 'user__full_name__icontains'],
        'location': 'user__location',
        'language': 'languages',
        'certification': 'certification_roles',
    }

    def filter_by_partner(self, value):
        return Q(
            user__partners_roles__partner=value,
            user__partners_roles__status=settings.RELATION_ROLE_CH_ACTIVE,
        )

    def filter_by_status(self, value):
        consultant_statuses = [
            settings.CONSULTANT_STATUS_CH_ACTIVE,
            settings.CONSULTANT_STATUS_CH_DISABLED,
        ]
        if value in consultant_statuses:
            return Q(status=value)
        else:
            processes = RegistrationProcess.objects.filter_by_current_status(
                value).values_list('user__consultant__id', flat=True)
            return Q(id__in=processes)

    def filter_by_permission_codename(self, permissions_list):
        for perm_to_filter in permissions_list:
            queryset = self.filter(user__user_permissions__codename=perm_to_filter)
        return queryset

    def not_disabled(self):
        return self.exclude(status=settings.CONSULTANT_STATUS_CH_DISABLED)

    def filter_showing_web(self, type_site):
        return self.filter(public_sites__icontains=type_site)

    def users(self):
        consultant_ids = self.values_list('id', flat=True)
        return get_user_model().objects.filter(consultant__id__in=consultant_ids)

    def exclude_in_waiting_list(self):
        return self.exclude(
            user__groups__name=settings.CONSULTANT_WAITING_LIST_GROUP_NAME)

    def filter_consulting_enabled(self):
        return self.filter_by_permission_codename(
            permissions_list=[settings.EXO_ACTIVITY_CH_ACTIVITY_CONSULTING],
        ).distinct()

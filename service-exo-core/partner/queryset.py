from guardian.shortcuts import get_objects_for_user

from utils.queryset import QuerySetFilterComplexMixin

from .conf import settings


class PartnerQuerySet(QuerySetFilterComplexMixin):

    _fields_from_form = {
        'search': [
            'name__icontains',
        ],
    }

    def filter_by_user(self, user):
        partners_ids = get_objects_for_user(user, settings.PARTNER_FULL_VIEW_PARTNER).values_list('id', flat=True)
        return self.filter(id__in=partners_ids)

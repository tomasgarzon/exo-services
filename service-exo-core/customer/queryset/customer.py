from guardian.shortcuts import get_objects_for_user

from entity.querysets import EntityQuerysetMixin

from ..conf import settings


class CustomerQuerySet(EntityQuerysetMixin):

    def filter_by_user(self, user):
        customers_ids = get_objects_for_user(user, settings.CUSTOMER_FULL_VIEW_CUSTOMER).values_list('id', flat=True)
        return self.filter(id__in=customers_ids)

    def type_normal(self):
        return self.filter(customer_type=settings.CUSTOMER_CH_NORMAL)

    def filter_no_partners(self):
        return self.filter(partners__isnull=True)

    def filter_by_partner(self, partner):
        return self.filter(partners=partner)

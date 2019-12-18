from partner.models import Partner

from .entity_user import EntityUserQuerySet


class PartnerUserQuerySet(EntityUserQuerySet):
    def filter_by_partner(self, partner):
        return self.filter(partner=partner)

    def partners(self):
        partner_ids = self.values_list('partner_id', flat=True)
        return Partner.objects.filter(id__in=partner_ids)

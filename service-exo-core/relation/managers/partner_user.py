from .role import RoleManager
from ..queryset.partner_user import PartnerUserQuerySet


class PartnerUserRoleManager(RoleManager):

    queryset_class = PartnerUserQuerySet

    def get_args_for_create(self, user, role):
        args = {
            'partner': self.instance,
            'user': user,
        }
        return args

    def filter_by_partner(self, partner):
        return self.get_queryset().filter_by_partner(partner)

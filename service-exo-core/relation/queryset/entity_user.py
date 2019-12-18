from .role import RoleQuerySet
from ..conf import settings


class EntityUserQuerySet(RoleQuerySet):

    def filter_by_user(self, user):
        return self.filter(user=user)

    def has_admin_role(self):
        return settings.RELATION_ROLE_CH_ADMIN in self.values_list('role', flat=True)

    def has_regular_role(self):
        return settings.RELATION_ROLE_CH_REGULAR in self.values_list('role', flat=True)

from django.core.exceptions import ValidationError
from django.conf import settings

from .users import UserRolesMixin


class PartnerUserRolesMixin(UserRolesMixin):

    def can_add_user(self, user_from):
        if not user_from.has_perm(settings.PARTNER_ADD_USER, self):
            raise ValidationError('User {} has no perms to add partner user'.format(user_from))

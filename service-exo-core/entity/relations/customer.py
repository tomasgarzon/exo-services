from django.core.exceptions import ValidationError
from django.conf import settings

from .users import UserRolesMixin


class CustomerUserRolesMixin(UserRolesMixin):

    def can_add_user(self, user_from):
        if not user_from.has_perm(settings.CUSTOMER_ADD_USER, self):
            raise ValidationError('User {} has no perms to add customer'.format(user_from))

    def can_delete_user(self, user_from):
        if not user_from.has_perm(settings.CUSTOMER_EDIT_CUSTOMER, self):
            raise ValidationError('User {} has no perms to delete customer'.format(user_from))

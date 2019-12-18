from .role import RoleManager
from ..queryset.customer_user import CustomerUserQuerySet


class CustomerUserRoleManager(RoleManager):
    queryset_class = CustomerUserQuerySet

    def get_args_for_create(self, user, role):
        args = {
            'customer': self.instance,
            'user': user,
        }
        return args

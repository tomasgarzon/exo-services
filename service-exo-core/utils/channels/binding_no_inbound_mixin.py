class BindingNoInboundMixin:

    def has_permission(self, user, action, pk):
        # returning False no user will be able to update/create/delete object from realtime
        return False

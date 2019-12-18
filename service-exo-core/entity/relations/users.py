from invitation.models.mixins.invitation_model_mixin import InvitationModelMixin


class UserRolesMixin(InvitationModelMixin):

    def add_user(self, user_from, user_to, role, *args, **kwargs):
        """
        Generate a new user associated to this customer. If invitation is True,
        we will have to create an invitation too.
        Parameters:
        - user_to: user to add
        - role: role associated
        - invitation (optional): true or false, if we want to create an invitation
        - user_from (mandatory): user that invites/add role to user_to
        - status (optional): status the role will be created
        """

        self.can_add_user(user_from)
        new_role, _ = self.users_roles.get_or_create_role(
            user_to,
            role,
            status=kwargs.get('status', None),
        )
        do_invitation = kwargs.get('invitation', False)
        invitation = None

        if do_invitation:
            invitation = self.generate_role_invitation(
                user_from=user_from,
                user_to=user_to,
                role=new_role,
                days=kwargs.get('days', None),
            )
        return [new_role, invitation]

    def delete_user(self, user_from, email):
        self.can_delete_user(user_from)
        self.users_roles.get(user__email=email).delete()

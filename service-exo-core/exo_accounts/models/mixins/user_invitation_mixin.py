import logging


logger = logging.getLogger('user')


class UserInvitationMixin:
    def cancel(self, user_from, description):
        self.set_unusable_password()
        self.save()

    # ##
    # Invitation methods
    # ##

    def can_activate(self, user_from):
        """
        Check who can activate the user object
        """
        return not self.is_active

    def can_deactivate(self, user_from):
        """
        Check who can deactivate the user object
        """
        return self.is_active

    def activate(self, user_from, **kwargs):
        """
        Activates an Inactive User
        """
        if not self.is_active and self.can_activate(user_from):
            self.is_active = True
            self.save(update_fields=['is_active'])
            logger.info('User activated: {}'.format(self.email))

    def deactivate(self, user_from, description=None):
        """
        Deactivate the User
        """
        if self.is_active and self.can_deactivate(user_from):
            self.is_active = False
            self.set_unusable_password()
            self.save(update_fields=['is_active', 'password'])
            logger.info('User deactivated: {}'.format(self.email))

    def reactivate(self, user_from, description=None):
        # Not implemented
        pass

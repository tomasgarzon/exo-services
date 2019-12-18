class ApplicationInvitationMixin:

    def send_notification(self, invitation):
        return None

    def get_public_url(self, invitation):
        return ''

    def create_invitation(self):
        raise NotImplementedError

    def reactivate(self, user_from):
        self.send(user_from)

    def restart_invitation(self, user_from):
        raise NotImplementedError

    def remove_invitation(self, user_from):
        raise NotImplementedError

    @property
    def invitations_related(self):
        raise NotImplementedError

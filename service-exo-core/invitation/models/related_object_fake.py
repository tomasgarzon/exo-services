from django.db import models


class RelatedObjectFake(models.Model):
    def send_notification(self, invitation):
        pass

    def activate(self, user, *args, **kwargs):
        pass

    def deactivate(self, invitation, *args, **kwargs):
        pass

    def get_public_url(self, invitation):
        pass

    def mark_as_pending(self, *args, **kwargs):
        pass

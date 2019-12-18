from django.db.models import Manager

from ..conf import settings


class InvitationPendingManager(Manager):

    def get_queryset(self):
        return super().get_queryset().filter(
            status=settings.INVITATION_STATUS_CH_PENDING,
        )

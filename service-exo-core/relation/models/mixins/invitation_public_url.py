from django.urls import reverse
from django.core.exceptions import ValidationError

from invitation.models import Invitation


class InvitationPublicURLMixin:

    CUSTOM_ADD_PERMISSION = None

    def get_public_url(self, invitation=None):
        # NO Tested
        return ''
        if not invitation:
            try:
                invitations = Invitation.objects.filter_by_object(self)
                invitation = invitations[0]
            except IndexError:
                raise ValidationError('Wrong public url access')
        return reverse(
            'accept-invitation-relation',
            args=[invitation.hash],
        )

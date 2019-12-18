from rest_framework import mixins, viewsets

from djangorestframework_camel_case.render import CamelCaseJSONRenderer
from rest_framework.exceptions import PermissionDenied

from ..serializers.invitation_retrieve import InvitationRetrieveSerializer
from ...models import Invitation


class InvitationRetrieveViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    model = Invitation
    renderer_classes = (CamelCaseJSONRenderer, )
    serializer_class = InvitationRetrieveSerializer
    lookup_field = 'hash'
    lookup_url_kwarg = 'hash'

    def get_invitation(self):
        return self.model.objects.get(hash=self.kwargs['hash'])

    def get_queryset(self):
        invitation = self.get_invitation()
        if invitation.is_signup:
            return self.model.objects.filter_by_status_pending()
        else:
            if not self.request.user.is_authenticated:
                raise PermissionDenied
            return self.request.user.invitations.filter_by_status_not_cancelled()

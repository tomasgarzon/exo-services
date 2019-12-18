from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from guardian.mixins import PermissionRequiredMixin

from utils.api.doc_mixin import APIObjectMixin

from ...models import Invitation
from ..serializers.invitation import InvitationSerializer
from ..serializers.resend_invitation_user import ResendInvitationUserSerializer
from ...conf import settings


class ResendInvitationMixin(
        PermissionRequiredMixin,
        APIObjectMixin,
        GenericAPIView
):
    model = Invitation
    permission_required = settings.INVITATION_RESEND
    queryset = Invitation.objects.all()
    return_404 = True


class ResendInvitationView(ResendInvitationMixin):
    lookup_field = 'pk'
    lookup_url_kwarg = 'pk'
    serializer_class = InvitationSerializer

    def put(self, request, pk):
        invitation = self.get_object()
        invitation.resend(request.user)
        serializer = self.serializer_class(instance=invitation)
        return Response(serializer.data)


class ResendInvitationUserView(ResendInvitationMixin):
    lookup_field = 'pk'
    lookup_url_kwarg = 'pk'
    serializer_class = ResendInvitationUserSerializer

    def put(self, request, pk):
        invitation = self.get_object()
        data = {'email': request.data.get('email'), 'invitation': pk}
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        invitation.resend(request.user)
        return Response(data)

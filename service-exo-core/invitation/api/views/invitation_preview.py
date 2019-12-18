from rest_framework.views import APIView
from rest_framework.response import Response

from consultant.models import ConsultantValidation

from ..serializers.invitation_preview import InvitationPreviewSerializer
from ...models import Invitation


class InvitationPreviewView(APIView):
    serializer_class = InvitationPreviewSerializer

    def get(self, request):
        serializer = self.serializer_class(data=request.GET)
        if serializer.is_valid():
            validation_type = serializer.validated_data.get('validation_type')
            if Invitation.is_consultant_validation_type(validation_type):
                consultant_validation = ConsultantValidation.objects.get(
                    name=validation_type,
                )
                preview = consultant_validation.preview_notification(
                    name=serializer.validated_data.get('name', '<name>'),
                    description=serializer.validated_data.get('custom_text'),
                )
                return Response(preview)
            return Response('OK')
        return Response(serializer.errors)

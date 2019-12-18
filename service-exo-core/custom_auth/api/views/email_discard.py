from django.conf import settings

from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from exo_accounts import models

from ..serializers import DiscardEmailSerializer


class DiscardEmailView(generics.GenericAPIView):
    serializer_class = DiscardEmailSerializer
    permission_classes = (IsAuthenticated,)
    model = models.EmailAddress

    def post(self, request, format=None):
        serializer = self.get_serializer(data=self.request.data)

        serializer.is_valid(raise_exception=True)

        new_email = serializer.validated_data.get('email')
        new_email.delete()

        data = {'status': status.HTTP_200_OK,
                'code': settings.EXO_ACCOUNTS_EMAIL_VALIDATION.get(
                    settings.EXO_ACCOUNTS_VALIDATION_CHOICES_DISCARTED),
                'code_status': settings.EXO_ACCOUNTS_VALIDATION_CHOICES_DISCARTED}

        return Response(data)

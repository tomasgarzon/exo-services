from django.conf import settings

from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from exo_accounts import models

from ..serializers import ResendEmailAddressEmailSerializer


class ResendVerificationMailView(generics.GenericAPIView):

    serializer_class = ResendEmailAddressEmailSerializer
    model = models.EmailAddress
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):

        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        new_email = serializer.validated_data.get('email')
        user = serializer.validated_data.get('user')

        email = models.EmailAddress.objects.get(user=user, email=new_email)
        email.send_verification()

        data = {'status': status.HTTP_200_OK,
                'code': settings.EXO_ACCOUNTS_EMAIL_VALIDATION.get(
                    settings.EXO_ACCOUNTS_VALIDATION_CHOICES_PENDING),
                'code_status': settings.EXO_ACCOUNTS_VALIDATION_CHOICES_PENDING}

        return Response(data)

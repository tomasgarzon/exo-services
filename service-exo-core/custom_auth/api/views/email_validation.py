from django.conf import settings
from django.contrib.auth import get_user_model

from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..serializers import ValidateEmailSerializer


User = get_user_model()


class ValidateEmailView(generics.GenericAPIView):

    serializer_class = ValidateEmailSerializer
    permission_classes = (IsAuthenticated,)
    model = User

    def post(self, request, format=None):

        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        code = settings.EXO_ACCOUNTS_VALIDATION_CHOICES_VERIFIED
        message = settings.EXO_ACCOUNTS_EMAIL_VALIDATION.get(code, '')

        data = {
            'status': status.HTTP_200_OK,
            'code_status': code,
            'code': message,
        }

        return Response(data)

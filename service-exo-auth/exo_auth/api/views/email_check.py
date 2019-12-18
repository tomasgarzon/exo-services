from django.contrib.auth import get_user_model

from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..serializers.email_address import CheckEmailSerializer


User = get_user_model()


class CheckEmailView(generics.GenericAPIView):

    serializer_class = CheckEmailSerializer
    permission_classes = (IsAuthenticated,)
    model = User

    def post(self, request, format=None):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        return Response(status=status.HTTP_200_OK)

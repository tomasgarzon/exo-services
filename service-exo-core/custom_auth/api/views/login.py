from django.contrib.auth import (
    login as django_login
)

from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny

from frontend.helpers import UserRedirectController

from ...jwt_helpers import _build_jwt as jwt_encode

from ..serializers.auth import (
    LoginSerializer, JWTSerializer
)


class LoginView(GenericAPIView):
    """
    Check the credentials and return the REST Token
    if the credentials are valid and authenticated.
    Calls Django Auth login method to register User ID
    in Django session framework

    Accept the following POST parameters: username, password
    Return the REST Framework Token Object's key.
    """
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def process_login(self):
        django_login(self.request, self.user)

    def get_response_serializer(self):
        return JWTSerializer

    def login(self):
        self.user = self.serializer.validated_data['user']
        self.token = jwt_encode(self.user)
        self.process_login()

    def get_response(self):
        serializer_class = self.get_response_serializer()
        url, _ = UserRedirectController.redirect_url(self.user)
        data = {
            'token': self.token,
            'url': url,
        }
        serializer = serializer_class(
            instance=data,
            context={'request': self.request},
        )

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        self.request = request
        self.serializer = self.get_serializer(data=self.request.data)
        self.serializer.is_valid(raise_exception=True)
        self.login()
        return self.get_response()

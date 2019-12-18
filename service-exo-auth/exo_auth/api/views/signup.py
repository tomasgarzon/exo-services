from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import isAuthenticated

from ..serializers.signup import SignupSerializer


class SignupView(GenericAPIView):
    permission_classes = (isAuthenticated,)
    serializer_class = SignupSerializer

    def post(self, request, *args, **kwargs):
        self.request = request
        self.serializer = self.get_serializer(data=self.request.data)
        self.serializer.is_valid(raise_exception=True)
        return Response()

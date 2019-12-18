from djangorestframework_camel_case.render import CamelCaseJSONRenderer
from rest_framework import generics, response, status

from ..serializers.auth import LoginSerializer
from ..serializers.contracting_data import UserPaymentDataSerializer


class GetContractingDataView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    renderer_classes = (CamelCaseJSONRenderer, )

    def post(self, request, *args, **kwargs):
        self.request = request
        self.serializer = self.get_serializer(data=self.request.data)
        self.serializer.is_valid(raise_exception=True)
        user = self.serializer.validated_data.get('user')
        return self.get_response(user)

    def get_response_serializer(self):
        return UserPaymentDataSerializer

    def get_response(self, user):
        serializer_class = self.get_response_serializer()
        serializer = serializer_class(
            instance=user,
            context={'request': self.request},
        )
        return response.Response(serializer.data, status=status.HTTP_200_OK)

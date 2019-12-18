from rest_framework import status, serializers
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from account_config.api.views.config_param import ConfigParamMixin
from account_config.models import ConfigParam


class ConsultantConsentSerializer(serializers.Serializer):
    value = serializers.BooleanField(required=True)

    def create(self, validated_data):
        return ConsultantConsentAPIView(**validated_data)

    def update(self, instance, validated_data):
        pass


class ConsultantConsentAPIView(APIView, ConfigParamMixin):
    permission_classes = (IsAuthenticated,)
    serializer_class = ConsultantConsentSerializer

    def post(self, request, format=None):
        serializer = ConsultantConsentSerializer(data=request.data)
        if not serializer.is_valid():
            raise ValidationError(serializer.error_messages)

        param = ConfigParam.objects.get(name='image_consent')

        user = request.user
        if user.is_consultant:
            user = user.consultant

        if not param.allowed_agent(user):
            raise PermissionDenied

        param.set_value_for_agent(user, serializer.data.get('value'))
        return Response(None, status=status.HTTP_201_CREATED)

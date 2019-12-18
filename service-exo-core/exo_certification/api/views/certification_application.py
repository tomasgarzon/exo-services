from djangorestframework_camel_case import render, parser

from rest_framework import viewsets, mixins, status, exceptions
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from ..serializers import certification_application, certification_application_user
from ...models import CertificationRequest


class CertificationRequestViewSet(
        mixins.CreateModelMixin,
        mixins.UpdateModelMixin,
        viewsets.GenericViewSet):
    renderer_classes = (render.CamelCaseJSONRenderer, )
    parser_classes = (parser.CamelCaseJSONParser, )
    permission_classes = (AllowAny, )
    queryset = CertificationRequest.objects.all()
    serializers = {
        'create': certification_application.DraftCertificationSerializer,
        'update': certification_application.PendingCertificationSerializer,
        'draft_existing_user': certification_application_user.DraftCertificationUserSerializer,
    }

    def get_serializer_class(self):
        return self.serializers.get(
            self.action,
            self.serializers.get('create'),
        )

    @action(detail=False, methods=['post'], url_name='existing-user', url_path='auth')
    def draft_existing_user(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def handle_exception(self, exc):
        if isinstance(exc, (exceptions.NotAuthenticated,
                            exceptions.AuthenticationFailed)):
            return Response(exc.detail, status=exc.status_code)
        return super().handle_exception(exc)

from django.conf import settings
from django.contrib.auth import (
    login as django_login
)

from djangorestframework_camel_case import parser, render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny

from invitation.models import Invitation
from frontend.helpers import UserRedirectController

from ..serializers.join import JoinUsSerializer
from ..serializers.signup import SignupSerializer

from ...jwt_helpers import _build_jwt


class SignupView(GenericAPIView):
    lookup_field = 'hash'
    lookup_url_kwarg = 'hash'
    serializer_class = SignupSerializer
    permission_classes = (AllowAny,)
    swagger_schema = None

    def get_queryset(self):
        return Invitation.objects.filter(type=settings.INVITATION_TYPE_SIGNUP)

    def get_serializer_context(self):
        data = super().get_serializer_context()
        data['invitation'] = self.get_object()
        return data

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        django_login(request, user)
        next_url, _ = UserRedirectController.redirect_url(self.get_object().user)
        data = {
            'nextUrl': next_url,
            'token': _build_jwt(user)
        }
        return Response(data, status=status.HTTP_200_OK)


class JoinUsView(GenericAPIView):
    serializer_class = JoinUsSerializer
    renderer_classes = (render.CamelCaseJSONRenderer, )
    parser_classes = (parser.CamelCaseJSONParser, )
    permission_classes = (AllowAny, )

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        django_login(request, user)
        next_url, _ = UserRedirectController.redirect_url(user)
        data = {
            'next_url': next_url,
            'token': _build_jwt(user)
        }
        return Response(data, status=status.HTTP_200_OK)

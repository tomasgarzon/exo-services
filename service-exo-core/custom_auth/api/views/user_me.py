from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from rest_framework import generics, views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from djangorestframework_camel_case.render import CamelCaseJSONRenderer

from utils.drf.authentication import UsernameAuthentication
from frontend.helpers import UserRedirectController

from ..serializers import UserSerializer, UserUUIDSerializer
from ..serializers.group import GroupSerializer


class UserMeViewMixin(generics.ListAPIView):
    model = get_user_model()
    permission_classes = (IsAuthenticated,)

    def list(self, *args, **kwargs):
        return super().list(*args, **kwargs)

    def get_queryset(self):
        return self.model.objects.filter(id=self.request.user.id)


class UserMeView(UserMeViewMixin):
    serializer_class = UserSerializer
    renderer_classes = (CamelCaseJSONRenderer, )


class UserByUuidView(generics.RetrieveAPIView):
    model = get_user_model()
    serializer_class = UserUUIDSerializer
    renderer_classes = (CamelCaseJSONRenderer, )
    authentication_classes = (UsernameAuthentication, )
    permission_classes = (IsAuthenticated,)
    lookup_field = 'uuid'
    lookup_url_kwarg = 'uuid'

    @method_decorator(cache_page(10))
    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)

    def get_queryset(self):
        return self.model.objects.all()


class GroupByName(generics.RetrieveAPIView):
    model = Group
    serializer_class = GroupSerializer
    authentication_classes = (UsernameAuthentication, )
    permission_classes = (IsAuthenticated,)
    lookup_field = 'name'
    lookup_url_kwarg = 'name'

    def get_queryset(self):
        return self.model.objects.all()


class UserRedirectUrlView(views.APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = request.user
        next_url, zone = UserRedirectController.redirect_url(user)
        data = {'nextUrl': next_url, 'hardLink': zone}
        return Response(data)

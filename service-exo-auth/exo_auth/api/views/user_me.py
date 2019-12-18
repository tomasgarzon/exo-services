from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from utils.drf.authentication import UsernameAuthentication

from ..serializers.user import UserSerializer, UserUUIDSerializer


class UserMeViewMixin(generics.ListAPIView):
    model = get_user_model()
    permission_classes = (IsAuthenticated,)

    def list(self, *args, **kwargs):
        return super().list(*args, **kwargs)

    def get_queryset(self):
        return self.model.objects.filter(id=self.request.user.id)


class UserMeView(UserMeViewMixin):
    serializer_class = UserSerializer


class UserByUuidView(generics.RetrieveAPIView):
    model = get_user_model()
    serializer_class = UserUUIDSerializer
    authentication_classes = (UsernameAuthentication, )
    permission_classes = (IsAuthenticated,)
    lookup_field = 'uuid'
    lookup_url_kwarg = 'uuid'

    @method_decorator(cache_page(30))
    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)

    def get_queryset(self):
        return self.model.objects.all()

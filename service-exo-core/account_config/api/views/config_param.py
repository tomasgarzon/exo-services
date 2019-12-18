from rest_framework import generics, permissions
from guardian.mixins import PermissionRequiredMixin

from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from ..serializers.config_param import (
    ConfigParamSerializer, ConfigParamUserSerializer)
from ...models import ConfigParam


User = get_user_model()


class ConfigParamMixin:
    lookup_field = 'pk'
    lookup_url_kwarg = 'pk'

    def get_agent(self):
        user = get_object_or_404(
            User,
            **{self.lookup_field: self.kwargs.get(self.lookup_url_kwarg)})
        if user.is_consultant:
            self.agent = user.consultant
        else:
            self.agent = user
        return self.agent

    def get_queryset(self):
        agent = self.get_agent()
        model_str = '{}.{}'.format(
            agent._meta.app_label,
            agent._meta.object_name)
        groups = settings.ACCOUNT_CONF_GROUPS
        names = []
        for key, values in groups.get(model_str, {}).items():
            names.extend(values)
        return ConfigParam.objects.filter(
            name__in=names)


class ConfigParamUserListView(
        PermissionRequiredMixin,
        ConfigParamMixin, generics.ListAPIView):

    permission_classes = (permissions.IsAuthenticated, )
    model = ConfigParam
    serializer_class = ConfigParamSerializer
    permission_required = settings.EXO_ACCOUNTS_PERMS_USER_EDIT
    return_404 = True
    swagger_schema = None

    def get_permission_object(self):
        return get_object_or_404(
            User, **{self.lookup_field: self.kwargs.get(self.lookup_url_kwarg)})

    def get_serializer_context(self, *args, **kwargs):
        context = super().get_serializer_context(*args, **kwargs)
        context['agent'] = self.get_agent()
        return context


class ConfigParamUserbyUUIDListView(ConfigParamUserListView):
    lookup_field = 'uuid'
    lookup_url_kwarg = 'user_uuid'
    swagger_schema = None


class ConfigParamUserCreateView(
        PermissionRequiredMixin,
        ConfigParamMixin, generics.CreateAPIView):

    model = ConfigParam
    serializer_class = ConfigParamUserSerializer
    permission_required = settings.EXO_ACCOUNTS_PERMS_USER_EDIT
    return_404 = True
    swagger_schema = None

    def get_permission_object(self):
        return get_object_or_404(User, pk=self.kwargs.get('pk'))

    def get_object(self):
        self.config_param = get_object_or_404(self.get_queryset(), pk=self.kwargs.get('config_pk'))
        return self.config_param

    def get_serializer_context(self, *args, **kwargs):
        self.get_object()
        context = super().get_serializer_context(*args, **kwargs)
        context['agent'] = self.get_agent()
        return context

    def perform_create(self, serializer):
        serializer.save(
            config_param=self.config_param,
        )

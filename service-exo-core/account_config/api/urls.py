from django.urls import path

from .views import config_param

app_name = 'account_config'

urlpatterns = [
    path(
        'config_param/<int:pk>/',
        config_param.ConfigParamUserListView.as_view(),
        name='config-param',
    ),
    path(
        'config_param/<uuid:user_uuid>/',
        config_param.ConfigParamUserbyUUIDListView.as_view(),
        name='config-param-uuid',
    ),
    path(
        'config_param/<int:pk>/update/<int:config_pk>/',
        config_param.ConfigParamUserCreateView.as_view(),
        name='config-param-update',
    ),
]

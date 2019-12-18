"""
service URL Configuration
"""
import re

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.urls import re_path

from django.views.static import serve

from utils import api_view

from .docs import schema_view


urlpatterns = []

if settings.ADMIN_PANEL:
    urlpatterns += [
        path('RPQ5j3T1MyfN0exiwOUZ/', admin.site.urls),
    ]

urlpatterns += [
    path('api/', include('payments.api.urls', namespace='api')),
    path('backup/', api_view.BackupAPIView.as_view()),
    path('health/', include('health_check.api.urls')),
    path('', include('payments.urls', namespace='payments')),
]

urlpatterns += [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

prefix = '/media/'
kwargs = {'document_root': settings.MEDIA_ROOT}
urlpatterns += [
    re_path(r'^%s(?P<path>.*)$' % re.escape(prefix.lstrip('/')), serve, kwargs=kwargs),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

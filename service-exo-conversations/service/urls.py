"""
service URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings

from utils import api_view

from .docs import schema_view


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api', include('conversations.api.urls')),
    path('files/', include('files.urls')),
    path('backup/', api_view.BackupAPIView.as_view()),
    path('health/', include('health_check.api.urls')),
]

urlpatterns += [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

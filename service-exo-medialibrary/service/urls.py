"""exolibrary URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from utils import api_view

from .docs import schema_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('resource/', include('resource.urls', namespace='resource')),
    path('api/', include('service.urls_api', namespace='api')),
    path('health/', include('health_check.api.urls')),
    path('backup/', api_view.BackupAPIView.as_view()),
]

urlpatterns += [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

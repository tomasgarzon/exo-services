"""

OpenExO URL Configuration

"""

from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from utils.loader import load_class
from utils.graphene.views import (
    CustomPublicGraphQLView,
    CustomAuthenticatedGraphQLView,
)

from ..docs import schema_view


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^graphql/$',
        CustomAuthenticatedGraphQLView.as_view(
            graphiql=settings.DEBUG_GRAPHQL)
        ),
    url(r'^public-graphql/$',
        CustomPublicGraphQLView.as_view(
            graphiql=True,
            schema=load_class('service.schema.public_schema'),
        )),
    url(r'^api/', include('service.urls.urls_api', namespace='api')),
    url(r'^customer/', include('customer.urls', namespace='customer')),
    url(r'^partner/', include('partner.urls', namespace='partner')),
    url(r'^network/', include('consultant.urls', namespace='consultant')),
    url(r'^project/', include('project.urls')),
    url(r'^certification/', include('custom_auth.certification_urls', namespace='certification')),
    url(r'^public/', include('service.urls.urls_public', namespace='public')),
    url(r'^tool/', include('tools.urls', namespace='tools')),
    url(r'^files/', include('files.urls', namespace='files')),
    url(r'^home/', include('dashboard.urls', namespace='dashboard')),
    url(r'^typeform/', include('typeform.urls', namespace='typeform')),
    url(r'^health/', include('health_check.api.urls')),
    url(r'^', include('frontend.urls')),
]

urlpatterns += [
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if getattr(settings, 'MICROSERVICES_DOCKER', False):
    urlpatterns += [
        url(r'^', include('service.urls.urls_services')),
    ]

if settings.DEBUG:
    urlpatterns += [
        url(r'^', include('service.urls.urls_debug')),
    ]

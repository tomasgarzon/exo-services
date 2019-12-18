from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from .views.files import ResourceUploadView, UserResourceUploadView
from .views.resource import ResourceViewSet


app_name = 'files'

router_resource = DefaultRouter()
router_resource.register(r'resources', ResourceViewSet)


urlpatterns = [
    url(r'^resources/', include(router_resource.urls)),
    url(r'^resource-upload/$', ResourceUploadView.as_view()),
    url(
        r'^user-resource-upload/$',
        UserResourceUploadView.as_view(), name='user-upload',
    ),
]

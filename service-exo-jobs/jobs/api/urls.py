from django.conf.urls import url, include

from rest_framework.routers import DefaultRouter

from .views import job

app_name = 'api'

router = DefaultRouter()

router.register('admin', job.AdminJobViewSet, basename='admin')
router.register('', job.JobViewSet, basename='job')


urlpatterns = [
    url(r'', include(router.urls)),
]

from django.conf.urls import url, include

from rest_framework.routers import DefaultRouter

from .views import exo_activity

app_name = 'exo-activity'

router = DefaultRouter()
router.register(
    r'list',
    exo_activity.ExOActivityViewSet,
    basename='activity',
)

urlpatterns = [
    url(r'', include(router.urls)),
]

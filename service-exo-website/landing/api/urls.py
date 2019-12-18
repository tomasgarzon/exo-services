from rest_framework import routers

from . import views

app_name = 'landing'

router = routers.SimpleRouter()

router.register('page', views.PageViewSet, basename="page")
router.register(
    'public-page',
    views.PublicPageViewSet, basename="public-page")

urlpatterns = router.urls

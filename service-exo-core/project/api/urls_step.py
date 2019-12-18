from rest_framework import routers

from .views import step

app_name = 'project'

router = routers.SimpleRouter()

router.register('', step.StepViewSet, basename='step')

urlpatterns = router.urls

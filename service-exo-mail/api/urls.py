from rest_framework import routers

from .views import message

app_name = 'api'

router = routers.SimpleRouter()

router.register('config', message.ConfigMailViewSet, basename="config")
router.register('mail', message.SendMailViewSet, basename="mail")


urlpatterns = router.urls

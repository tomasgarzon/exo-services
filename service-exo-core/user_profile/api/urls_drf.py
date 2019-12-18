from rest_framework import routers

from .views import profile_public

app_name = 'profile'

router = routers.SimpleRouter()


router.register('', profile_public.UserProfilePublicView, basename='profile')

urlpatterns = router.urls

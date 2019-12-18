from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import agreement

app_name = 'agreement'

router = DefaultRouter()


router.register(r'exq', agreement.ExQAgreementViewSet, basename='exq')


urlpatterns = [
    path('', include(router.urls)),
]

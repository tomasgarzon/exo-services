from django.conf.urls import url, include

from rest_framework.routers import DefaultRouter

from .views import service_request, agreement

app_name = 'marketplace'

router = DefaultRouter()

router.register(
    r'service-request',
    service_request.ServiceRequestViewSet,
    basename='service-request',
)

router.register(
    r'agreement',
    agreement.MarketplaceAgreementViewSet,
    basename='agreement',
)


urlpatterns = [
    url(r'', include(router.urls)),
]

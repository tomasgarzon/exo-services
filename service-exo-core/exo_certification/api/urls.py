from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from .views import (
    CohortListView,
    certification_application,
    certification_webhooks,
)


router = DefaultRouter()
router.register(
    r'application',
    certification_application.CertificationRequestViewSet,
    basename='applications'
)
router.register(
    r'webhooks/payment',
    certification_webhooks.CertificationRequestPaymentWebhookViewSet,
    basename='webhooks',
)

app_name = 'exo-certification'

urlpatterns = [
    url(r'^cohort/$', CohortListView.as_view(), name='cohorts'),
]

urlpatterns += [
    url(r'^', include(router.urls)),
]

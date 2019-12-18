from django.conf.urls import url

from rest_framework.routers import DefaultRouter

from .views.consultant_consent import ConsultantConsentAPIView
from .views.consultant_autocomplete import ConsultantSearchViewSet
from .views import network_actions

app_name = 'consultant'

router = DefaultRouter()
router.register(r'consultant-autocomplete', ConsultantSearchViewSet, basename='autocomplete')

urlpatterns = router.urls

urlpatterns += [
    # network actions
    url(
        r'^delete/(?P<pk>\d+)/$',
        network_actions.DeleteConsultantView.as_view(),
        name='delete',
    ),
    url(
        r'^reactivate/(?P<pk>\d+)/$',
        network_actions.ReactivateConsultantView.as_view(),
        name='reactivate',
    ),
    url(
        r'^add/$',
        network_actions.ConsultantAddView.as_view(),
        name='create',
    ),
    url(
        r'^consent/$',
        ConsultantConsentAPIView.as_view(),
        name='consent',
    )
]

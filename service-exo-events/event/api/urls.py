from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views.event import EventViewSet
from .views.event_management import EventStatusViewSet
from .views.participant import ParticipantViewSet, ParticipantPublicViewSet, ParticipantBadgesViewSet
from .views.event_public import PublicEventSearchViewSet, PublicEventView
from .views.interested import InterestedListViewSet, InterestedCreateAPIView

app_name = 'event'

router = DefaultRouter()
router.register('manage', EventStatusViewSet, basename='event')
router.register('', EventViewSet, basename='event')

router2 = DefaultRouter()
router2.register('', ParticipantViewSet, basename='participant')

router3 = DefaultRouter()
router3.register('', InterestedListViewSet, basename='interested')

urlpatterns = [
    path('participant-badges/', ParticipantBadgesViewSet.as_view(), name='participant-badges'),
    path('search/', PublicEventSearchViewSet.as_view(), name='search'),
    path('public-event/<uuid:event_id>', PublicEventView.as_view(), name='public'),
    path('interested/create/', InterestedCreateAPIView.as_view(), name='interested-create'),
    path('participants-public/', ParticipantPublicViewSet.as_view(), name='participant-public-create'),
    path('participants/<uuid:event_id>/', include(router2.urls)),
    path('interested/<uuid:event_id>/', include(router3.urls)),
    path('', include(router.urls)),
]

from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from .views import followers, circle

app_name = 'circles'

router = DefaultRouter()
router.register(
    r'',
    circle.ForumCircleViewSet,
    basename='circles'
)

urlpatterns = [
    url(
        r'^',
        include(router.urls)
    ),
    url(
        r'^(?P<slug>[-\w \W]+)/followers/$',
        followers.FollowersAPIView.as_view(),
        name='followers'
    ),
    url(
        r'^(?P<slug>[-\w \W]+)/mentions/$',
        followers.MentionsAPIView.as_view(),
        name='mentions'
    ),
]

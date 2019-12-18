from django.conf.urls import url

from .views.member_public import MemberPublicListAPIView

app_name = 'ecosystem-public'

urlpatterns = [
    url(
        r'^members/$',
        MemberPublicListAPIView.as_view(),
        name='members',
    ),
]

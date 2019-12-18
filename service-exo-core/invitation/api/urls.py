from django.conf.urls import url, include

from rest_framework.routers import DefaultRouter

from .views import (
    invitation_preview,
    invitation_resend,
    invitation_retrieve,
    invitation
)

app_name = 'invitation'

router_invitation = DefaultRouter()
router_invitation.register(r'invitation', invitation.InvitationViewSet)
router_invitation.register(
    r'boarding',
    invitation_retrieve.InvitationRetrieveViewSet,
    basename='boarding',
)

urlpatterns = [
    url(
        r'^preview/$',
        invitation_preview.InvitationPreviewView.as_view(),
        name='preview-email',
    ),
    url(
        r'^resend/(?P<pk>\d+)/$',
        invitation_resend.ResendInvitationView.as_view(),
        name='resend-email',
    ),
    url(
        r'^resend-user/(?P<pk>\d+)/$',
        invitation_resend.ResendInvitationUserView.as_view(),
        name='resend-user',
    ),
    url(r'', include(router_invitation.urls)),
]

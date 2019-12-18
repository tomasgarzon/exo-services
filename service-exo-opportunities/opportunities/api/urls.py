from django.urls import path, include

from rest_framework import routers

from .views import (
    opportunity, applicant, user, webhook, group, roles,
    view_opportunity, migrate_ticket)


app_name = 'opportunities'

router = routers.SimpleRouter()

router.register(
    r'opportunity',
    opportunity.OpportunityViewSet,
    basename='opportunity',
)
router.register(
    r'opportunity-group/(?P<group_id>\d+)',
    opportunity.OpportunityGroupViewSet,
    basename='opportunity-group',
)
router.register(
    r'opportunity-badges',
    opportunity.OpportunityBadgesViewSet,
    basename='opportunity-badges',
)
router.register(
    r'applicant',
    applicant.ApplicantViewSet,
    basename='applicant',
)

router.register(
    r'user',
    user.UserUUIDViewSet,
    basename='user',
)

router.register(
    r'group',
    group.OpportunityGroupViewSet,
    basename='group')

router.register(
    r'webhook',
    webhook.OpportunityWebhookViewSet,
    basename='webhook')

router.register(
    r'admin-opportunity',
    view_opportunity.OpportunityRetrieveViewSet,
    basename='opportunity-admin')

router.register(
    r'groups',
    group.OpportunityGroupUserViewSet,
    basename='groups')


urlpatterns = [
    path('', include(router.urls)),
    path(
        'roles/',
        roles.CategoryListView.as_view(), name='roles'),
    path(
        'opportunities-migrate/',
        migrate_ticket.MigrateTicketViiew.as_view(), name='migrate')
]

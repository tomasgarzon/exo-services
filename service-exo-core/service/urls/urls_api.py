from django.conf.urls import url, include
from django.conf import settings

from utils.graphene.views import CustomAuthenticatedJWTGraphQLView

app_name = 'api'

urlpatterns = [
    url(r'^agreement/', include('agreement.api.urls')),
    url(r'^graphql-jwt/$',
        CustomAuthenticatedJWTGraphQLView.as_view(graphiql=settings.DEBUG)),
    url(r'^core/', include('core.api.urls')),
    url(r'^frontend/', include('frontend.api.urls')),
    url(r'^consultant/',
        include('consultant.api.urls', namespace='consultant')),
    url(r'^files-versioned/',
        include('files.api.urls_uploaded_file', namespace='file-versioned')),
    url(r'^files/', include('files.api.urls', namespace='file')),
    url(r'^relation/', include('relation.api.urls', namespace='relation')),
    url(r'^profile/(?P<pk>\d+)/', include('user_profile.api.urls', namespace='profile')),
    url(r'^profile-public/', include('user_profile.api.urls_drf', namespace='profile-public')),
    url(r'^industries/', include('industry.api.urls')),
    url(r'^learning/', include('learning.api.urls', namespace='learning')),
    url(r'^project/', include('project.api.urls', namespace='project')),
    url(r'^registration/',
        include('registration.api.urls', namespace='registration')),
    url(r'^invitation/',
        include('invitation.api.urls', namespace='invitation')),
    url(r'^accounts/', include('custom_auth.api.urls', namespace='accounts')),
    url(r'^zoom/', include('zoom_project.urls', namespace='zoom')),
    url(r'^internal-messages/',
        include('exo_messages.api.urls', namespace='internal-messages')),
    url(r'^keywords/', include('keywords.api.urls', namespace='keywords')),
    url(r'^forum/', include('forum.api.urls', namespace='forum')),
    url(r'^account-config/', include('account_config.api.urls', namespace='account-config')),
    url(r'^mentions/', include('mentions.api.urls', namespace='mentions')),
    url(r'^circles/', include('circles.api.urls', namespace='circles')),
    url(r'^marketplace/', include('marketplace.api.urls', namespace='marketplace')),
    url(r'^ecosystem/', include('ecosystem.api.urls', namespace='ecosystem')),
    url(r'^ecosystem-public/', include('ecosystem.api.public_urls', namespace='ecosystem-public')),
    url(r'^swarms/', include('qa_session.api.urls', namespace='swarms')),
    url(r'^exo-activity/', include('exo_activity.api.urls', namespace='exo-activity')),
    url(r'^exo-certification/', include('exo_certification.api.urls', namespace='exo-certification')),
    url(r'^exo-role/', include('exo_role.api.urls', namespace='exo-role')),
    url(r'^certifications/', include('exo_certification.api.urls_certifications', namespace='certifications')),
    url(r'^referral/', include('referral.api.urls', namespace='referral')),
    url(r'^typeform/', include('typeform_feedback.api.urls', namespace='typeform')),
]

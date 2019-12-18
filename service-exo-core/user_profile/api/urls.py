from django.conf.urls import url

from .views import (
    consultant, contracting, conversation,
    email, image, profile, password,
    user_language_platform,
)

app_name = 'profile'


urlpatterns = [
    url(
        r'^change-password/$',
        password.SetPasswordView.as_view(),
        name='change-password',
    ),
    url(
        r'^platform-language/$',
        user_language_platform.UserLanguagePlattformView.as_view(),
        name='change-platform-language',
    ),
    url(
        r'^update-image-profile/$',
        image.UpdateImageProfileView.as_view(),
        name='change-image',
    ),
    url(
        r'^update-email/$',
        email.UpdateEmailView.as_view(),
        name='change-email',
    ),
    url(
        r'^update-contracting-data/$',
        contracting.UpdateContractingView.as_view(),
        name='change-contracting',
    ),
    url(
        r'^update-profile-summary/$',
        profile.UpdateProfileSummaryView.as_view(),
        name='change-profile-summary',
    ),
    url(
        r'^update-profile-languages/$',
        consultant.UpdateLanguagesProfileView.as_view(),
        name='change-profile-languages',
    ),
    url(
        r'^update-profile-mtp/$',
        consultant.UpdateMTPProfileView.as_view(),
        name='change-profile-mtp',
    ),
    url(
        r'^update-profile-core-pillars/$',
        consultant.UpdateCorePillarsProfileView.as_view(),
        name='change-profile-core-pillars',
    ),
    url(
        r'^update-profile-availability/$',
        consultant.UpdateTimeAvailabilityProfileView.as_view(),
        name='change-profile-availability',
    ),
    url(
        r'^update-profile-activities/$',
        consultant.UpdateActivitiesProfileView.as_view(),
        name='change-profile-activities',
    ),
    url(
        r'^update-profile-exo-attributes/$',
        consultant.UpdateExOAttributesProfileView.as_view(),
        name='change-profile-exo-attributes',
    ),
    url(
        r'^update-profile-industries/$',
        consultant.UpdateIndustryProfileView.as_view(),
        name='change-profile-industries',
    ),
    url(
        r'^update-profile-keywords/$',
        consultant.UpdateKeywordProfileView.as_view(),
        name='change-profile-keywords',
    ),
    url(
        r'^update-profile-video/$',
        consultant.UpdateProfileVideoView.as_view(),
        name='update-profile-video',
    ),
    url(
        r'^start-conversation/$',
        conversation.StartConversationView.as_view(),
        name='start-conversation',
    ),
    # version 2
    url(
        r'^summary/$',
        profile.ProfileSummaryView.as_view(),
        name='summary',
    ),
    url(
        r'^about-you/$',
        profile.ProfileAboutYouView.as_view(),
        name='about-you',
    ),
]

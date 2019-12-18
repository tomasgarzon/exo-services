from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views.email_validation import ValidateEmailView
from .views.email_discard import DiscardEmailView
from .views.email_resend import ResendVerificationMailView
from .views.email_check import CheckEmailView
from .views import (
    user_me, login, logout, signup, requirements,
    request_contact, user, public_contracting_data,
    user_signup)

app_name = 'accounts'

router = DefaultRouter()
router.register(r'user', user.UserViewSet, basename='user')


urlpatterns = [
    path('me/', user_me.UserMeView.as_view(), name='me'),
    path('go-to/', user_me.UserRedirectUrlView.as_view(), name='go-to'),
    path('me/<uuid:uuid>/', user_me.UserByUuidView.as_view(), name='me-uuid'),
    path('groups/<slug:name>/', user_me.GroupByName.as_view(), name='group-name'),
    path('me/requirements/', requirements.UserRequirementView.as_view(), name='me-requirements'),
    path('check-email/', CheckEmailView.as_view(), name='check-email'),
    path('validate-email/', ValidateEmailView.as_view(), name='validate-email'),
    path('resend-email/', ResendVerificationMailView.as_view(), name='resend-email'),
    path('discard-email/', DiscardEmailView.as_view(), name='discard-email'),
    path('login/', login.LoginView.as_view(), name='rest_login'),
    path('logout/', logout.LogoutView.as_view(), name='rest_logout'),
    path('join-us/', signup.JoinUsView.as_view(), name='join-us'),
    path(
        'contracting-data/',
        public_contracting_data.GetContractingDataView.as_view(),
        name='public-contracting-data'),
    path('signup-auth/', user_signup.UserSignupView.as_view(), name='signup-auth'),
    path('signup/<str:hash>/', signup.SignupView.as_view(), name='signup'),
    path('request-contact/', request_contact.UserRequestContactView.as_view(), name='request-contact'),
    path('password/', include('custom_auth.api.url_recover_password', namespace='password')),
    path('', include(router.urls)),
]

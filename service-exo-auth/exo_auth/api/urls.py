from django.urls import path

from .views.email_validation import ValidateEmailView
from .views.email_discard import DiscardEmailView
from .views.email_resend import ResendVerificationMailView
from .views.email_check import CheckEmailView
from .views import (
    user_me, login, logout, password, migrate_user,
    realtime_user)


app_name = 'api'

urlpatterns = [
    path(
        'me/',
        user_me.UserMeView.as_view(),
        name='me'),
    path(
        'me/<uuid>[0-9a-f-]+/',
        user_me.UserByUuidView.as_view(), name='me-uuid'),
    path(
        'on_subscribe/',
        realtime_user.OnSubscribeView.as_view(),
        name='on-subscribe'),
    path(
        'on_unsubscribe/',
        realtime_user.OnUnsubscribeView.as_view(),
        name='on-unsubscribe'),
    path(
        'subscriptors/<subscription>/',
        realtime_user.UserSubscribeView.as_view(),
        name='subscriptors'),
    path('ticket/', realtime_user.UserJWTView.as_view(), name='ticket-jwt'),
    path('check-email/', CheckEmailView.as_view(), name='check-email'),
    path('validate-email/', ValidateEmailView.as_view(), name='validate-email'),
    path('resend-email/', ResendVerificationMailView.as_view(), name='resend-email'),
    path('discard-email/', DiscardEmailView.as_view(), name='discard-email'),

    path('login/', login.LoginView.as_view(), name='rest_login'),
    path('logout/', logout.LogoutView.as_view(), name='rest_logout'),
    path('migrate/', migrate_user.MigrateUserView.as_view(), name='migrate'),
    path(
        'password/change/',
        password.PasswordChangeView.as_view(),
        name='password-change',
    ),
    path(
        'password/request-change/',
        password.PasswordResetView.as_view(),
        name='password-request',
    ),
]

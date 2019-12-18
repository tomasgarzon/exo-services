from django.conf.urls import url

from .views import password

app_name = 'password'

urlpatterns = [
    url(
        r'^change/$',
        password.PasswordChangeView.as_view(),
        name='change',
    ),

    url(
        r'^request-change/$',
        password.PasswordResetView.as_view(),
        name='request',
    ),
]

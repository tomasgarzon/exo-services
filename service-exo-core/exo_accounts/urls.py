try:
    from django.conf.urls import url
except ImportError:
    from django.urls import re_path as url

from .views import multimail


# Django 2.0 declaration
app_name = 'exo_accounts'

urlpatterns = [
    url(r'^verify/(?P<email_pk>\d+)/(?P<verif_key>.+)/$',
        multimail.Verify.as_view(),
        name='email-verification-url'),
]

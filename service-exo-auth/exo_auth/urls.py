try:
    from django.conf.urls import url
except ImportError:
    from django.urls import re_path as url

from . import views

# Django 2.0 declaration
app_name = 'exo-auth'

urlpatterns = [
    url(r'^verify/(?P<email_pk>\d+)/(?P<verif_key>.+)/$',
        views.Verify.as_view(),
        name='email-verification-url'),
]

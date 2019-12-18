from django.conf.urls import url

from .views import certifications

app_name = 'certifications'

urlpatterns = [
    url(r'^$', certifications.CertsListView.as_view(), name='list'),
]

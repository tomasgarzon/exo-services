from django.conf.urls import url

from .views import AdminDashboardView

app_name = 'dashboard'

urlpatterns = [
    url(r'^$', AdminDashboardView.as_view(), name='home'),
]

from django.urls import path

from .views import resource_view

app_name = 'resource'


urlpatterns = [
    path('redirect/<str:handle>/<str:filename>/',
         resource_view.ResourceRedirectView.as_view(), name='resource-redirect')
]

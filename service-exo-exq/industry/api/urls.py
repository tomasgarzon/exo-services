from django.urls import path

from .views import (
    IndustryListAPIView,
)

app_name = 'industry'

urlpatterns = [
    path(
        'industry/', IndustryListAPIView.as_view(),
        name='list',
    ),
]

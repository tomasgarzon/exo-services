from django.urls import path

from .views import certification

app_name = 'certification'

urlpatterns = [
    path('join-level-1/<str:language>/', certification.JoinLevel1View.as_view(), name='level-1'),
    path('join-level-1/', certification.JoinLevel1View.as_view(), name='level-1'),
]

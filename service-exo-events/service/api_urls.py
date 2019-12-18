from django.urls import path, include

app_name = 'api'

urlpatterns = [
    path('event/', include('event.api.urls')),
]

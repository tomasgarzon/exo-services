from django.conf.urls import url, include

app_name = "api"

urlpatterns = [
    url(r'^landing/', include('landing.api.urls', namespace='landing'))
]

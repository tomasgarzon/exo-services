from django.conf.urls import url, include

app_name = "api"

urlpatterns = [
    url(r'^resources/', include('resource.api.urls', namespace='resources'))
]

from django.urls import path, include

app_name = 'webhook'

urlpatterns = [
    path('typeform/', include('typeform.urls_webhooks', namespace='typeform')),
]

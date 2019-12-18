from django.conf.urls import url, include

app_name = 'public'

urlpatterns = [
    url(r'^mail/', include('exo_accounts.urls', namespace='mails')),
    url(r'^webhooks/', include('service.urls.urls_webhooks', namespace='webhooks')),
    url(r'^performance/', include('utils.urls', namespace='performance')),
]

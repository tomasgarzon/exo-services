from django.conf.urls import url, include

app_name = 'tools'

urlpatterns = [
    url(r'^badge/', include('badge.urls', namespace='badge')),
    url(r'^relation/', include('relation.urls_tools', namespace='relation')),
    url(r'^exo-certification/', include('exo_certification.urls_tools', namespace='exo-certification')),
]

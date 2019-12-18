from django.conf.urls import url

from ..views import resource, uploaded_file

app_name = 'file'

urlpatterns = [
    url(
        r'^media/(?P<slug>.*)$',
        resource.ResourceDownload.as_view(),
        name='download',
    ),
    url(
        r'^versioned/(?P<hash>.*)$',
        uploaded_file.UploadedFileDownload.as_view(),
        name='versioned-download',
    ),
]

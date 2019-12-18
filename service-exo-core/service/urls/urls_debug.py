import debug_toolbar
import requests

from django.conf import settings
from django.conf.urls import url, include
from django.http import HttpResponse

app_name = 'debug'

frontend_bundle = 'http://s3.amazonaws.com/openexo/bundles/exo-frontend'
frontend_html = '{}/{}/index.html'.format(frontend_bundle, settings.SOURCE_NAME)
frontend_assets = '{}/{}/assets/i18n/en.json'.format(frontend_bundle, settings.SOURCE_NAME)

response_html = requests.get(frontend_html)

if response_html.status_code != 200:
    index_data = 'ERROR: No frontend for branch: {}'.format(settings.SOURCE_NAME)
else:
    index_data = response_html.text

response_assets = requests.get(frontend_assets)
en_json_data = response_assets.text

urlpatterns = [
    url(r'^__debug__/', include(debug_toolbar.urls)),
    url(r'assets/i18n/en.json$', lambda request: HttpResponse(
        en_json_data, content_type='application/json')),
    url('', lambda request: HttpResponse(index_data)),
]

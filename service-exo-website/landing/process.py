import json
import tempfile
import subprocess
import logging

from django.conf import settings

from .api.serializers import PageSerializer
from .workshop_api import get_json_for_hugo


logger = logging.getLogger('website')


def build(page):
    serializer = PageSerializer(instance=page)
    data = serializer.data
    data['uuid'] = str(page.uuid)
    data.update(get_json_for_hugo(page.page_type, page.uuid))
    return build_from_dict(data)


def build_preview(page_type, data, uuid):
    data['uuid'] = str(uuid)
    data['slug'] += '-preview'
    data.update(get_json_for_hugo(page_type, uuid))
    return build_from_dict(data, preview=True)


def build_from_dict(data, preview=False):
    data['domain'] = settings.EXO_WEBSITE_DOMAIN
    data['status'] = 'preview' if preview else 'publish'
    data['root'] = settings.EXOLEVER_HOST
    temp_file = tempfile.mktemp(suffix='.json')
    with open(temp_file, 'a') as page_fd:
        json.dump(data, page_fd)

    call_build_website(temp_file)
    return temp_file


def call_build_website(filename):
    BACKUP_REQUEST_BASH_CMD = 'sh'
    BACKUP_REQUEST_BASH_PROC = '{}/{}'.format(
        settings.BASE_DIR, 'build-site.sh')
    subprocess.call([
        BACKUP_REQUEST_BASH_CMD,
        BACKUP_REQUEST_BASH_PROC,
        filename,
    ])

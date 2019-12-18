from filestack import Client

from django.conf import settings


def upload(url_path):
    client = Client(settings.FILESTACK_KEY)
    file = client.upload(url=url_path)
    return file.url, file.get_metadata()

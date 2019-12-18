import requests

from django.conf import settings


URL_PROJECT_PUBLIC_RETRIEVE = 'api/project/public-project'


def get_workshop_json(uuid):
    URL_PROJECT_PUBLIC_RETRIEVE = 'api/project/public-project'
    url = "{}/{}/{}/".format(
        settings.EXOLEVER_HOST,
        URL_PROJECT_PUBLIC_RETRIEVE,
        str(uuid))
    response = requests.get(url)
    if response and response.status_code == requests.codes.ok:
        return response.json()
    return {}


def get_event_json(uuid):
    URL_PROJECT_PUBLIC_RETRIEVE = 'api/event/public-event'
    host = settings.SERVICE_EVENTS_HOST
    host = settings.EXOLEVER_HOST + host
    url = "{}{}/{}".format(
        host,
        URL_PROJECT_PUBLIC_RETRIEVE,
        str(uuid))
    response = requests.get(url)
    if response and response.status_code == requests.codes.ok:
        return response.json()
    return {}


def get_json_for_hugo(page_type, uuid):
    if page_type == settings.LANDING_CH_WORKSHOP:
        return get_workshop_json(uuid)
    else:
        return get_event_json(uuid)

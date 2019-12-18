from service.celery import app
from django.conf import settings

from utils import notifications


@app.task
def new_user_connected(uuids_in_topic, new_user_uuid):
    for uuid in uuids_in_topic:
        notifications.send_notifications(
            settings.EXO_AUTH_TOPIC_CONNECTED,
            settings.EXO_AUTH_USER_CONNECTED,
            {'uuid': uuid.__str__()},
            {'user_uuid': new_user_uuid})


@app.task
def user_disconnected(uuids_in_topic, removed_user_uuid):
    for uuid in uuids_in_topic:
        notifications.send_notifications(
            settings.EXO_AUTH_TOPIC_CONNECTED,
            settings.EXO_AUTH_USER_DISCONNECTED,
            {'uuid': uuid.__str__()},
            {'user_uuid': removed_user_uuid})

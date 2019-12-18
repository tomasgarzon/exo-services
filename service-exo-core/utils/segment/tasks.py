import json

import analytics
from celery import Task
from django.conf import settings
from djangorestframework_camel_case.render import CamelCaseJSONRenderer

analytics.debug = settings.DEBUG
analytics.write_key = settings.SEGMENT_WRITE_KEY


class SegmentIdentifyTask(Task):
    name = 'SegmentIdentifyTask'
    ignore_result = False

    def run(self, *args, **kwargs):
        uuid = kwargs.get('uuid')
        email = kwargs.get('email')
        name = kwargs.get('name')
        analytics.identify(uuid, {
            'email': email,
            'name': name,
        })


class SegmentEventTask(Task):
    name = 'SegmentEventTask'
    ignore_result = False

    def run(self, *args, **kwargs):
        uuid = kwargs.get('uuid')
        event = kwargs.get('event')
        payload = json.loads(CamelCaseJSONRenderer().render(kwargs.get('payload')))
        analytics.track(uuid, event, payload)

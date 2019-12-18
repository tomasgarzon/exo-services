# -*- coding: utf-8 -*-
# Generated for Django 2.2 on 2019-04-26 09:21
from __future__ import unicode_literals

import requests

from django.conf import settings

from exo_changelog import change, operations

from ..models import Opportunity


def find_place_id(location):
    # AIzaSyBfYpBR8NJD07Yn2NGzyj6wGRr6e6E0628
    url = 'https://maps.googleapis.com/maps/api/place/findplacefromtext/json'
    data = {
        'input': location,
        'key': 'AIzaSyC_7O2X1L92psvmJWcS_MW6hebrh_32_b4',
        'language': 'en',
        'inputtype': 'textquery',
        'fields': 'place_id'
    }
    if not settings.POPULATOR_MODE:
        try:
            return requests.get(url, params=data).json().get('candidates')[0].get('place_id')
        except Exception:
            return ''
    return ''


def populate_place_id():
    opportunities_to_fix = Opportunity.objects.filter(
        mode=settings.OPPORTUNITIES_CH_MODE_ONSITE,
    ).exclude(place_id__isnull=False)

    for opportuniy in opportunities_to_fix:
        opportuniy.place_id = find_place_id(opportuniy.location)
        opportuniy.save()


class Change(change.Change):

    dependencies = [
        ('opportunities', '0001_initial'),
    ]

    operations = [
        operations.RunPython(populate_place_id)
    ]

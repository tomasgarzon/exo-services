# -*- coding: utf-8 -*-
# Generated for Django 2.2.7 on 2019-11-21 15:35
from __future__ import unicode_literals

from django.conf import settings

from exo_changelog import change

from ..models import Event


migration_table = (
    ('B', 'Book Launch'),
    ('E', 'Webinar'),
)


def migrate_old_events_types():
    for migration in migration_table:
        Event.objects.filter(
            type_event=migration[0]
        ).update(
            type_event=settings.EXO_ROLE_CATEGORY_OTHER,
            type_event_other=migration[1]
        )


class Change(change.Change):

    dependencies = [
        ('event', '0001_initial'),
    ]

    operations = []

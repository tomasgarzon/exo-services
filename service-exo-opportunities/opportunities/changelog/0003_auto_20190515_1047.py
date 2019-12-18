# -*- coding: utf-8 -*-
# Generated for Django 2.2.1 on 2019-05-15 10:47
from __future__ import unicode_literals
from django.conf import settings

from exo_changelog import change, operations
from ..models import Opportunity


def migrate_assigned_opportunities():
    CH_ASSIGNED = 'C'
    new_status = settings.OPPORTUNITIES_CH_REQUESTED
    i = 0
    for opp in Opportunity.objects.filter(_status=CH_ASSIGNED):
        opp._status = new_status
        opp.save(update_fields=['_status'])
        opp.history.create(
            status=new_status,
            user=opp.created_by)
        i += 1
    print('Migrated {} opportunities'.format(i))


class Change(change.Change):

    dependencies = [
        ('opportunities', '0002_auto_20190426_0939'),
    ]

    operations = [
        operations.RunPython(migrate_assigned_opportunities)
    ]

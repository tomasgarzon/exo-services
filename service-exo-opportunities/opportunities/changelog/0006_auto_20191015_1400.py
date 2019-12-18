# -*- coding: utf-8 -*-
# Generated for Django 2.2.5 on 2019-10-15 14:00
from __future__ import unicode_literals

from exo_changelog import change, operations
from django.db.models import F

from ..models import Opportunity


def create_sent_at():
    Opportunity.objects.update(sent_at=F('created'))


class Change(change.Change):

    dependencies = [
        ('opportunities', '0005_auto_20190725_0957'),
    ]

    operations = [
        operations.RunPython(create_sent_at)
    ]

# -*- coding: utf-8 -*-
# Generated for Django 1.11.12 on 2019-01-15 15:31
from __future__ import unicode_literals

from django.conf import settings

from exo_changelog import change, operations

from ..models import Agreement


def migrate_brand():
    for agg in Agreement.objects.filter(name__icontains='ExO Lever'):
        agg.name = agg.name.replace('ExO Lever', settings.BRAND_NAME)
        agg.save(update_fields=['name'])


class Change(change.Change):

    dependencies = [
    ]

    operations = [
        operations.RunPython(migrate_brand)
    ]

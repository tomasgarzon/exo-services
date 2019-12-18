# -*- coding: utf-8 -*-
# Generated for Django 1.11.12 on 2019-01-15 15:34
from __future__ import unicode_literals

from django.conf import settings

from exo_changelog import change, operations

from ..models import InternalOrganization


def migrate_brand():
    # Organizations
    InternalOrganization.objects.filter(name='ExO Lever').update(name=settings.BRAND_NAME)


class Change(change.Change):

    dependencies = [
    ]

    operations = [
        operations.RunPython(migrate_brand)
    ]

# -*- coding: utf-8 -*-
# Generated for Django 1.11.12 on 2019-04-25 10:59
from __future__ import unicode_literals

from django.conf import settings

from exo_changelog import change, operations

from ..models import Agreement


def rename_agreement_for_advising():
    old_name = settings.BRAND_NAME + ' Consulting Agreement'
    new_name = 'Consulting Services Agreement'
    Agreement.objects.filter(name=old_name).update(name=new_name)


class Change(change.Change):

    dependencies = [
        ('agreement', '0001_initial'),
    ]

    operations = [
        operations.RunPython(rename_agreement_for_advising)
    ]

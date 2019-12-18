# -*- coding: utf-8 -*-
# Generated for Django 1.11.12 on 2019-04-29 15:10
from __future__ import unicode_literals
from django.core.management import call_command

from exo_changelog import change, operations


def create_or_update_hub():
    call_command('create_update_hub')


class Change(change.Change):

    dependencies = [
        ('exo_hub', '0003_auto_20190425_0800'),
    ]

    operations = [
        operations.RunPython(create_or_update_hub)
    ]

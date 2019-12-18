# -*- coding: utf-8 -*-
# Generated for Django 2.2.7 on 2019-11-27 15:11
from __future__ import unicode_literals

from exo_changelog import change, operations
from django.core.management import call_command


def refresh_data():
    call_command('loaddata', 'config_attributes.json')


class Change(change.Change):

    dependencies = [
        ('account_config', '0003_auto_20190311_1731'),
    ]

    operations = [
        operations.RunPython(refresh_data)
    ]

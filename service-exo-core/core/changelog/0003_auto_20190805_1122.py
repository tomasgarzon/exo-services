# -*- coding: utf-8 -*-
# Generated for Django 1.11.12 on 2019-08-05 11:22
from __future__ import unicode_literals

from django.core.management import call_command
from exo_changelog import change, operations


def import_countries():
    call_command('update_core_countries')


class Change(change.Change):
    dependencies = [
        ('core', '0002_auto_20190624_0729'),
    ]

    operations = [
        operations.RunPython(import_countries),
    ]

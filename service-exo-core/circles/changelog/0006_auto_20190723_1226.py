# -*- coding: utf-8 -*-
# Generated for Django 1.11.12 on 2019-07-23 12:26
from __future__ import unicode_literals

from django.core.management import call_command
from exo_changelog import change, operations


def update_circle_descriptions():
    call_command('update_circle_descriptions')


class Change(change.Change):

    dependencies = [
        ('circles', '0005_auto_20190704_1111'),
    ]

    operations = [
        operations.RunPython(update_circle_descriptions)
    ]

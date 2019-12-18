# -*- coding: utf-8 -*-
# Generated for Django 1.11.12 on 2019-04-25 07:39
from __future__ import unicode_literals

from django.core.management import call_command

from exo_changelog import change, operations


def update_exo_activities():
    call_command('update_or_create_exo_activities')


class Change(change.Change):

    dependencies = [
        ('exo_activity', '0001_initial'),
    ]

    operations = [
        operations.RunPython(update_exo_activities)
    ]

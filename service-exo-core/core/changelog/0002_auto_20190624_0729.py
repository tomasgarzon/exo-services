# -*- coding: utf-8 -*-
# Generated for Django 1.11.12 on 2019-06-24 07:29
from __future__ import unicode_literals

from django.core.management import call_command

from exo_changelog import change, operations


def update_core_languages():
    call_command('update_core_languages')


class Change(change.Change):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        operations.RunPython(update_core_languages)
    ]

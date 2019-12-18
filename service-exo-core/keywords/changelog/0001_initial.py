# -*- coding: utf-8 -*-
# Generated for Django 1.11.12 on 2019-01-16 08:05
from __future__ import unicode_literals

from exo_changelog import change, operations

from django.core.management import call_command


def update_technologies():
    filename = 'utils/scrapy/technologies.json'
    call_command('load_technologies', filename)


class Change(change.Change):

    dependencies = [
    ]

    operations = [
        operations.RunPython(update_technologies)
    ]

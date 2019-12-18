# -*- coding: utf-8 -*-
# Generated for Django 2.2.7 on 2019-12-17 16:10
from __future__ import unicode_literals

from django.core.management import call_command

from exo_changelog import change, operations


def delete_obsolete_tables():
    call_command('delete_ticket_tables')


class Change(change.Change):

    dependencies = [
        ('utils', '0005_auto_20191114_1243'),
    ]

    operations = [
        operations.RunPython(delete_obsolete_tables)
    ]

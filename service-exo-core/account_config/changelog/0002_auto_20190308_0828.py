# -*- coding: utf-8 -*-
# Generated for Django 1.11.12 on 2019-03-08 08:28
from __future__ import unicode_literals

from exo_changelog import change, operations


def refresh_data():
    pass


class Change(change.Change):

    dependencies = [
        ('account_config', '0001_initial'),
    ]

    operations = [
        operations.RunPython(refresh_data)
    ]

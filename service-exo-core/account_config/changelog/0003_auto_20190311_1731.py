# -*- coding: utf-8 -*-
# Generated for Django 1.11.12 on 2019-03-11 17:31
from __future__ import unicode_literals

from exo_changelog import change, operations


def refresh_data():
    pass


class Change(change.Change):

    dependencies = [
        ('account_config', '0002_auto_20190308_0828'),
    ]

    operations = [
        operations.RunPython(refresh_data)
    ]

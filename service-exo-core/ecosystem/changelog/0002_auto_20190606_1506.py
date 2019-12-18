# -*- coding: utf-8 -*-
# Generated for Django 1.11.12 on 2019-06-06 15:06
from __future__ import unicode_literals

from exo_changelog import change, operations


def update_ecosystem_members():
    pass


class Change(change.Change):

    dependencies = [
        ('ecosystem', '0001_initial'),
    ]

    operations = [
        operations.RunPython(update_ecosystem_members)
    ]

# -*- coding: utf-8 -*-
# Generated for Django 1.11.12 on 2019-01-15 15:33
from __future__ import unicode_literals

from exo_changelog import change, operations


def migrate_brand():
    pass


class Change(change.Change):

    dependencies = [
    ]

    operations = [
        operations.RunPython(migrate_brand)
    ]

# -*- coding: utf-8 -*-
# Generated for Django 2.2.7 on 2019-11-14 12:43
from __future__ import unicode_literals

from exo_changelog import change, operations


def delete_obsolete_tables():
    pass


class Change(change.Change):

    dependencies = [
        ('utils', '0004_auto_20191023_1443'),
    ]

    operations = [
        operations.RunPython(delete_obsolete_tables)
    ]

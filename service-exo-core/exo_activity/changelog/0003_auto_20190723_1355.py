# -*- coding: utf-8 -*-
# Generated for Django 1.11.12 on 2019-07-23 13:55
from __future__ import unicode_literals

from exo_changelog import change, operations


def migrate_ecosystem():
    pass


class Change(change.Change):

    dependencies = [
        ('exo_activity', '0002_auto_20190425_0739'),
    ]

    operations = [
        operations.RunPython(migrate_ecosystem)
    ]

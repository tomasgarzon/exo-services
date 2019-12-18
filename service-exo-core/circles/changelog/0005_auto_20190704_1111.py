# -*- coding: utf-8 -*-
# Generated for Django 1.11.12 on 2019-07-04 11:11
from __future__ import unicode_literals

from exo_changelog import change, operations


def rename_ecosytem_circle():
    pass


class Change(change.Change):

    dependencies = [
        ('circles', '0004_auto_20190520_1348'),
    ]

    operations = [
        operations.RunPython(rename_ecosytem_circle)
    ]

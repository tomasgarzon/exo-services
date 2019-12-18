# -*- coding: utf-8 -*-
# Generated for Django 1.11.12 on 2018-09-19 05:19
from __future__ import unicode_literals

from exo_changelog import change, operations


def add_consultant_to_marketplace():
    pass


class Change(change.Change):

    dependencies = [
        ('circles', '0001_initial'),
    ]

    operations = [
        operations.RunPython(add_consultant_to_marketplace)
    ]

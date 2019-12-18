# -*- coding: utf-8 -*-
# Generated for Django 1.11.12 on 2019-04-25 14:50
from __future__ import unicode_literals

from exo_changelog import change, operations


def update_ecosystem():
    pass


class Change(change.Change):

    dependencies = [
    ]

    operations = [
        operations.RunPython(update_ecosystem)
    ]

# -*- coding: utf-8 -*-
# Generated for Django 1.11.12 on 2018-10-18 07:19
from __future__ import unicode_literals

from exo_changelog import change, operations


def load_initial_data():
    pass


class Change(change.Change):

    dependencies = []

    operations = [
        operations.RunPython(load_initial_data)
    ]

# -*- coding: utf-8 -*-
# Generated for Django 1.11.12 on 2018-12-02 19:52
from __future__ import unicode_literals

from exo_changelog import change, operations


def migrate_project():
    pass


class Change(change.Change):

    dependencies = [
    ]

    operations = [
        operations.RunPython(migrate_project)
    ]

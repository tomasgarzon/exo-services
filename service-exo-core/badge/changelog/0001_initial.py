# -*- coding: utf-8 -*-
# Generated for Django 1.11.12 on 2019-09-10 09:45
from __future__ import unicode_literals

from exo_changelog import change, operations


def create_user_badges():
    pass


class Change(change.Change):

    dependencies = []

    operations = [
        operations.RunPython(create_user_badges)
    ]

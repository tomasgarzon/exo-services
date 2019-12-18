# -*- coding: utf-8 -*-
# Generated for Django 1.11.12 on 2018-11-29 14:26
from __future__ import unicode_literals

from exo_changelog import change, operations


def create_feedback_circle_add_all_users():
    pass


class Change(change.Change):

    dependencies = [
        ('circles', '0002_auto_20180919_0519'),
    ]

    operations = [
        operations.RunPython(create_feedback_circle_add_all_users)
    ]

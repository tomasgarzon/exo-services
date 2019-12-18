# -*- coding: utf-8 -*-
# Generated for Django 1.11.12 on 2019-08-27 06:33
from __future__ import unicode_literals

from exo_changelog import change, operations


def update_user_title():
    pass


class Change(change.Change):

    dependencies = [
        ('exo_accounts', '0003_auto_20190524_0748'),
    ]

    operations = [
        operations.RunPython(update_user_title)
    ]

# -*- coding: utf-8 -*-
# Generated for Django 1.11.12 on 2018-08-29 10:24
from __future__ import unicode_literals

from exo_changelog import change, operations


def say_hello():
    print('Hello')


class Change(change.Change):

    dependencies = [
    ]

    operations = [
        operations.RunPython(say_hello)
    ]

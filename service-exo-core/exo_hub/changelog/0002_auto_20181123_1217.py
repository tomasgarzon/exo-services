# -*- coding: utf-8 -*-
# Generated for Django 1.11.12 on 2018-11-23 12:17
from __future__ import unicode_literals

from exo_changelog import change


class Change(change.Change):

    dependencies = [
        ('exo_hub', '0001_initial'),
    ]

    operations = []

# -*- coding: utf-8 -*-
# Generated for Django 2.2.5 on 2019-10-03 11:30
from __future__ import unicode_literals

from exo_changelog import change


class Change(change.Change):

    dependencies = [
        ('exo_certification', '0001_initial'),
    ]

    operations = []

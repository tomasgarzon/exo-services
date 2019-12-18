# -*- coding: utf-8 -*-
# Generated for Django 2.2.1 on 2019-05-20 09:17
from __future__ import unicode_literals

from exo_changelog import change


class Change(change.Change):

    dependencies = [
        ('opportunities', '0003_auto_20190515_1047'),
    ]

    operations = []

# -*- coding: utf-8 -*-
# Generated for Django 2.2.3 on 2019-07-25 09:57
from __future__ import unicode_literals

from exo_changelog import change


class Change(change.Change):

    dependencies = [
        ('opportunities', '0004_auto_20190520_0917'),
    ]

    operations = []

# -*- coding: utf-8 -*-
# Generated for Django 2.2.7 on 2019-11-18 14:51
from __future__ import unicode_literals

from exo_changelog import change, operations
from ..circle_helper import adding_certification_required


class Change(change.Change):

    dependencies = [
        ('circles', '0007_auto_20190726_0610'),
    ]

    operations = [
        operations.RunPython(adding_certification_required)
    ]

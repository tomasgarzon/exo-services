# -*- coding: utf-8 -*-
# Generated for Django 2.2.6 on 2019-10-17 10:12
from __future__ import unicode_literals

from exo_changelog import change, operations


def sync_customer_training_jobs():
    pass


class Change(change.Change):

    dependencies = [
        ('job', '0001_initial'),
    ]

    operations = [
        operations.RunPython(sync_customer_training_jobs)
    ]

# -*- coding: utf-8 -*-
# Generated for Django 2.2 on 2019-04-26 09:21
from __future__ import unicode_literals

from exo_changelog import change, operations

from ..models import Opportunity


def migrate_budget_coins():
    for opportunity in Opportunity.objects.filter(budget_currency='C'):
        opportunity.virtual_budget = opportunity.budget
        opportunity.budget = ''
        opportunity.budget_currency = None
        opportunity.save()


class Change(change.Change):

    dependencies = [
    ]

    operations = [
        operations.RunPython(migrate_budget_coins)
    ]

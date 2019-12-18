# -*- coding: utf-8 -*-
# Generated for Django 2.2.5 on 2019-09-19 14:10
from __future__ import unicode_literals


from exo_changelog import change, operations


STRIPE_PAYMENTS_TO_CANCEL = [
    'C190007', 'C190008', 'C190012', 'C190016', 'C190021', 'C190024', 'C190030',   # Real payments
    'C190046', 'C190065', 'C190068', 'C190083',
    'C190001', 'C190002', 'C190003', 'C190004', 'C190006', 'C190010', 'C190011',   # Test payments
    'C190013', 'C190035', 'C190036', 'C190037', 'C190048', 'C190055', 'C190109',
    'C190117', 'C190125', 'C190126', 'C190127', 'C190128', 'C190129', 'C190130',
    'C190151', 'C190166',
]


def cancel_old_pending_payments():
    pass


class Change(change.Change):

    dependencies = [
        ('payments', '0001_initial'),
    ]

    operations = [
        operations.RunPython(cancel_old_pending_payments)
    ]

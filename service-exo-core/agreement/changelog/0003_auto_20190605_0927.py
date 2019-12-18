# -*- coding: utf-8 -*-
# Generated for Django 1.11.12 on 2019-06-05 09:27
from __future__ import unicode_literals

from django.conf import settings

from exo_changelog import change, operations

from ..models import Agreement


def revoke_consulting_agreement():
    ag = Agreement.objects.filter_by_domain_activity().filter_by_status_active().first()
    if ag:
        ag.set_status(settings.AGREEMENT_STATUS_INACTIVE)


class Change(change.Change):

    dependencies = [
        ('agreement', '0002_auto_20190425_1059'),
    ]

    operations = [
        operations.RunPython(revoke_consulting_agreement)
    ]

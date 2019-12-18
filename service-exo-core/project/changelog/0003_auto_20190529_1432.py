# -*- coding: utf-8 -*-
# Generated for Django 1.11.12 on 2019-05-29 14:32
from __future__ import unicode_literals
from django.conf import settings

from exo_changelog import change
from project.models import Project
from project.signals_define import project_category_changed_signal


PROJECT_CATEGORY_EVENT = 'E'


def populate_project_category():
    Project.objects.filter(customer__isnull=True).update(
        category=PROJECT_CATEGORY_EVENT)
    for project in Project.objects.filter(customer__isnull=False):
        if project.customer.training:
            project.category = settings.PROJECT_CH_CATEGORY_TRAINING
            project.save(update_fields=['category'])
            project_category_changed_signal.send(
                sender=Project,
                instance=project)


class Change(change.Change):

    dependencies = [
        ('project', '0002_auto_20190430_0809'),
    ]

    operations = []

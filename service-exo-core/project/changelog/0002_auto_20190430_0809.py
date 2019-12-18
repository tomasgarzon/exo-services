# -*- coding: utf-8 -*-
# Generated for Django 1.11.12 on 2019-04-30 08:09
from __future__ import unicode_literals
from django.conf import settings

from exo_changelog import change, operations
from ..models import Project


def populate_template():

    for project in Project.objects.all():
        type_project = project.type_verbose_name.upper()
        template_name = settings.PROJECT_TYPE_TO_TEMPLATE.get(type_project)
        if template_name:
            Project.objects.filter(pk=project.pk).update(template=template_name)


class Change(change.Change):

    dependencies = [
        ('project', '0001_initial'),
    ]

    operations = [
        operations.RunPython(populate_template)
    ]

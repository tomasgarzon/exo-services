# -*- coding: utf-8 -*-
# Generated for Django 1.11.12 on 2019-06-27 14:27
from __future__ import unicode_literals

from exo_changelog import change, operations
from certification.models import CertificationGroup


def populate_instructor_name():
    for group in CertificationGroup.objects.filter(instructor_name__isnull=True):
        if group.content_object and group.content_object.created_by:
            group.instructor_name = group.content_object.created_by.get_full_name()
            group.save()
        elif group.created_by:
            group.instructor_name = group.created_by.get_full_name()
            group.save()


class Change(change.Change):

    dependencies = [
        ('project', '0003_auto_20190529_1432'),
    ]

    operations = [
        operations.RunPython(populate_instructor_name)
    ]

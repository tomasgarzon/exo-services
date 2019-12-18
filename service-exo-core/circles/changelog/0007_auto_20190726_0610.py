# -*- coding: utf-8 -*-
# Generated for Django 1.11.12 on 2019-07-26 06:10
from __future__ import unicode_literals

from django.conf import settings
from exo_changelog import change, operations

from circles.models import Circle


def remove_feedback_circle():
    pass


def mark_default_circles_as_certified():
    circles = Circle.objects.filter(created_by__isnull=True)

    for circle in circles:
        if circle.slug in settings.CIRCLES_CERTIFIED_CIRCLE_SLUGS:
            circle.type = settings.CIRCLES_CH_TYPE_CERTIFIED
            circle.save()
            print('{} circle marked as certified'.format(circle.name))
        else:
            circle.type = settings.CIRCLES_CH_TYPE_SECRET
            circle.save()
            print('{} circle marked as secret'.format(circle.name))


class Change(change.Change):

    dependencies = [
        ('circles', '0006_auto_20190723_1226'),
    ]

    operations = [
        operations.RunPython(remove_feedback_circle),
        operations.RunPython(mark_default_circles_as_certified),
    ]

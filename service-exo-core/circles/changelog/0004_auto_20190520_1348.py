# -*- coding: utf-8 -*-
# Generated for Django 1.11.12 on 2019-05-20 13:48
from __future__ import unicode_literals

from django.core.management import call_command
from exo_changelog import change


def set_circle_images():
    call_command('regenerate_circle_images')


class Change(change.Change):

    dependencies = [
        ('circles', '0003_auto_20181129_1426'),
    ]

    operations = []

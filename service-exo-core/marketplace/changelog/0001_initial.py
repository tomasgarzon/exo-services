# -*- coding: utf-8 -*-
# Generated for Django 1.11.12 on 2018-09-20 11:56
from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

from exo_changelog import change, operations


def create_marketplace_group():
    emails = [
        'francisco@openexo.com',
        'lars@openexo.com',
        'zahra@openexo.com',
        'javier.munoz@openexo.com',
    ]
    users = get_user_model().objects.filter(email__in=emails)
    group, _ = Group.objects.get_or_create(name=settings.MARKETPLACE_GROUP_NAME)
    for user in users:
        group.user_set.add(user)


class Change(change.Change):

    dependencies = [
    ]

    operations = [
        operations.RunPython(create_marketplace_group),
    ]

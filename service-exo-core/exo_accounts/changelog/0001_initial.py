# -*- coding: utf-8 -*-
# Generated for Django 1.11.12 on 2019-04-09 17:38
from __future__ import unicode_literals

from django.contrib.auth import get_user_model

from exo_changelog import change, operations    # noqa


def generate_new_sizes():
    for user in get_user_model().objects.all():
        user.profile_picture.generate_thumbnails()


class Change(change.Change):

    dependencies = [
    ]

    operations = []     # noqa

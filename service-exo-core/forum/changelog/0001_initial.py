# -*- coding: utf-8 -*-
# Generated for Django 1.11.12 on 2019-07-03 10:05
from __future__ import unicode_literals

from exo_changelog import change, operations

from forum.models import Post


def delete_team_step_posts():
    posts = Post.objects.filter(_type='T')
    total = posts.count()
    posts.delete()
    print('\n{} project step post(s) have been removed.'.format(total))


class Change(change.Change):

    dependencies = [
    ]

    operations = [
        operations.RunPython(delete_team_step_posts)
    ]

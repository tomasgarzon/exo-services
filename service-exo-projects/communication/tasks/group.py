from django.apps import apps
from django.contrib.auth import get_user_model

from celery import Task

from ..conversation_helper import (
    create_group,
    update_group,
    delete_group)


class GroupCreateTask(Task):
    name = 'GroupCreateTask'
    ignore_result = True

    def run(self, *args, **kwargs):
        Group = apps.get_model('communication', 'Group')
        group = Group.objects.get(pk=kwargs.get('group_id'))
        user_from = get_user_model().objects.get(pk=kwargs.get('user_id'))
        create_group(group, user_from)


class GroupUpdateTask(Task):
    name = 'GroupUpdateTask'
    ignore_result = True

    def run(self, *args, **kwargs):
        Group = apps.get_model('communication', 'Group')
        group = Group.objects.get(pk=kwargs.get('group_id'))
        user_from = get_user_model().objects.get(pk=kwargs.get('user_id'))
        update_group(group, user_from)


class GroupDeleteTask(Task):
    name = 'GroupDeleteTask'
    ignore_result = True

    def run(self, *args, **kwargs):
        Group = apps.get_model('communication', 'Group')
        group = Group.objects.get(pk=kwargs.get('group_id'))
        user_from = get_user_model().objects.get(pk=kwargs.get('user_id'))
        delete_group(group, user_from)

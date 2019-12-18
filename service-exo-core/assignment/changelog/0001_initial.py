# -*- coding: utf-8 -*-
# Generated for Django 1.11.12 on 2018-12-03 13:33
from __future__ import unicode_literals

from django.conf import settings

from exo_changelog import change, operations

from ..models import AssignmentResourceItem


def fix_wrong_assignments():
    link = 'EwIpHgeVQOm9vZmLp2Q7'
    print('Change wrong resources with {} link'.format(link))

    items = AssignmentResourceItem.objects.filter(link__icontains=link)
    core_link = '7EW9Ir4kRPCAob6jUKQ0'
    edge_link = '8lkqjh6SMquewU1JpqRE'

    for item in items:
        content_object = item.assignment_resource.block.content_object
        class_name = content_object.__class__.__name__
        resource_streams = None

        if class_name == 'AssignmentStep':
            resource_streams = content_object.streams
        elif class_name == 'AssignmentTaskItem':
            resource_streams = content_object.assignment_task.block.content_object.streams

        if resource_streams:
            if settings.PROJECT_STREAM_CH_STARTUP in resource_streams:
                item.link = item.link.replace(link, edge_link)
            elif settings.PROJECT_STREAM_CH_STRATEGY in resource_streams:
                item.link = item.link.replace(link, core_link)

            item.save()

    print('Resources with wrong links updated')


class Change(change.Change):

    dependencies = [
    ]

    operations = [
        operations.RunPython(fix_wrong_assignments)
    ]

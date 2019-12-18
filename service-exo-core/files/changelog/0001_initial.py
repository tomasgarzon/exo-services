# -*- coding: utf-8 -*-
# Generated for Django 1.11.12 on 2019-08-23 07:28
from __future__ import unicode_literals

from exo_changelog import change, operations
from django.contrib.contenttypes.models import ContentType
from django.db.utils import ProgrammingError
from files.models import UploadedFile
from django.db import connection
from collections import namedtuple


def namedtuplefetchall(cursor):
    """Return all rows from a cursor as a namedtuple"""
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]


def migrate_files():
    with connection.cursor() as cursor:
        try:
            cursor.execute('select parent_type_id,parent_id,object_type_id,object_id from genericm2m_relatedobject')
        except ProgrammingError:
            return
        results = namedtuplefetchall(cursor)
        for result in results:
            file = UploadedFile.objects.get(pk=result.parent_id)
            content_type = ContentType.objects.get(
                pk=result.object_type_id)
            try:
                related_object = content_type.model_class().objects.get(
                    pk=result.object_id)
            except content_type.model_class().DoesNotExist:
                continue
            file.related = related_object
            file.save()


class Change(change.Change):

    dependencies = [
    ]

    operations = [
        operations.RunPython(migrate_files)
    ]

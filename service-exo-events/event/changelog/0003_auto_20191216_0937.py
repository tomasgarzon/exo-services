# -*- coding: utf-8 -*-
# Generated for Django 2.2.8 on 2019-12-16 09:37
from __future__ import unicode_literals

from django.conf import settings
from django.core.management import call_command

from exo_role.models import Category, ExORole
from exo_changelog import change, operations

from ..models import Event, Participant


def update_exo_roles():
    call_command('update_or_create_roles')


def migrate_event_types():
    mapping = {
        'T': settings.EXO_ROLE_CATEGORY_TALK,
        'W': settings.EXO_ROLE_CATEGORY_WORKSHOP,
        'S': settings.EXO_ROLE_CATEGORY_SUMMIT,
        'O': settings.EXO_ROLE_CATEGORY_OTHER,
    }

    for old_event_type in mapping.keys():
        Event.all_objects.filter(
            type_event=old_event_type,
        ).update(
            category=Category.objects.get(code=mapping.get(old_event_type)),
        )


def fix_bad_roles_migrations():
    update_matrix = (
        (settings.EXO_ROLE_CODE_SUMMIT_SPEAKER, settings.EXO_ROLE_CODE_WORKSHOP_SPEAKER),
    )

    for update_case in update_matrix:
        Participant.objects.filter(
            role=update_case[0],
            event__type_event=settings.EXO_ROLE_CATEGORY_WORKSHOP,
        ).update(
            role=update_case[1],
        )


def migrate_roles():
    mapping = {
        settings.EXO_ROLE_CODE_CERTIFICATION_SPRINT_COACH: settings.EXO_ROLE_CODE_WORKSHOP_TRAINER,
        settings.EXO_ROLE_CODE_SUMMIT_COLLABORATOR: settings.EXO_ROLE_CODE_SUMMIT_COLLABORATOR,
        settings.EXO_ROLE_CODE_SUMMIT_COACH: settings.EXO_ROLE_CODE_SUMMIT_COACH,
        settings.EXO_ROLE_CODE_SUMMIT_ORGANIZER: settings.EXO_ROLE_CODE_SUMMIT_ORGANIZER,
        settings.EXO_ROLE_CODE_SUMMIT_SPEAKER: settings.EXO_ROLE_CODE_SUMMIT_SPEAKER,
    }

    for role in mapping.keys():
        Participant.objects.filter(
            role=role,
        ).update(
            exo_role=ExORole.objects.get(code=mapping.get(role)),
        )


class Change(change.Change):

    dependencies = [
        ('event', '0002_auto_20191121_1535'),
    ]

    operations = [
        operations.RunPython(update_exo_roles),
        operations.RunPython(migrate_event_types),
        operations.RunPython(fix_bad_roles_migrations),
        operations.RunPython(migrate_roles),
    ]

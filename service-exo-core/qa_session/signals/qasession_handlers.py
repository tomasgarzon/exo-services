from team.models import Team

from ..models import QASession

from ..reminder_helpers import (
    create_initial_reminder,
    clear_reminder)


def post_team_created_handler(sender, instance, created, *args, **kwargs):
    if created:
        for qa_session in QASession.objects.filter(project=instance.project):
            qa_session.teams.get_or_create(team=instance)


def post_qa_session_created_handler(sender, instance, created, *args, **kwargs):
    if created:
        for team in Team.objects.filter_by_project(instance.project):
            team.qa_sessions.get_or_create(session=instance)
        create_initial_reminder(instance)


def post_qa_session_delete_handler(sender, instance, *args, **kwargs):
    clear_reminder(instance)


def pre_save_qa_session(sender, instance, *args, **kwargs):
    if instance.pk:
        start_at = QASession.objects.get(pk=instance.pk).start_at
        end_at = QASession.objects.get(pk=instance.pk).end_at

        if start_at != instance.start_at or end_at != instance.end_at:
            clear_reminder(instance)

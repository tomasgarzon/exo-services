from django.apps import apps
from django.db.models.signals import post_save, post_delete, pre_save

from .qasession_handlers import (
    post_team_created_handler, post_qa_session_created_handler,
    post_qa_session_delete_handler,
    pre_save_qa_session)


def setup_signals():

    Team = apps.get_model(
        app_label='team', model_name='Team',
    )
    QASession = apps.get_model(
        app_label='qa_session', model_name='QASession',
    )

    post_save.connect(post_team_created_handler, sender=Team)
    post_save.connect(post_qa_session_created_handler, sender=QASession)
    pre_save.connect(pre_save_qa_session, sender=QASession)
    post_delete.connect(post_qa_session_delete_handler, sender=QASession)

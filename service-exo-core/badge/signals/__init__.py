from django.apps import apps
from django.db.models.signals import post_save, post_delete

from .relation import (
    consultant_project_role_post_save,
    consultant_project_role_post_delete,
    user_project_role_post_save,
    user_project_role_post_delete,
)


def setup_signals():
    # Models
    ConsultantProjectRole = apps.get_model(app_label='relation', model_name='ConsultantProjectRole')
    UserProjectRole = apps.get_model(app_label='relation', model_name='UserProjectRole')

    # Signals
    post_save.connect(
        consultant_project_role_post_save, sender=ConsultantProjectRole)
    post_delete.connect(
        consultant_project_role_post_delete, sender=ConsultantProjectRole)
    post_save.connect(
        user_project_role_post_save, sender=UserProjectRole)
    post_delete.connect(
        user_project_role_post_delete, sender=UserProjectRole)

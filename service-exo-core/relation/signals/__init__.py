from django.apps import apps
from django.db.models.signals import post_save, post_delete, pre_save

from project.signals_define import project_category_changed_signal

from .user_project import (
    user_project_role_post_save,
    user_project_role_post_delete
)
from .consultant_exo_activity import (
    activate_exo_activity_with_no_agreement,
    activate_deactivate_consultant_exo_activity_status
)
from .consultant_project import (
    consultant_project_role_post_save,
    consultant_project_role_post_delete,
    add_exo_consultant_to_project_handler,
)
from .consultant_role import (
    consultant_role_post_save,
    consultant_role_post_delete,
)
from ..signals_define import (
    signal_head_coach_created,
    signal_head_coach_removed,
    signal_user_assigned,
    signal_user_unassigned,
    add_user_exo_hub,
    remove_user_exo_hub,
    signal_add_exo_consultant_role,
)
from .head_coach_project import (
    add_head_coach_project,
    remove_head_coach_project
)
from .all_user_project import (
    all_user_project_when_added,
    all_user_project_when_removed,
    update_visible_roles,
    update_visible_project_role,
)

from .hub_user_handler import (
    hub_user_post_save_handler,
    hub_user_post_delete_handler)

from .user_exo_hub_handler import (
    add_user_to_exo_hub_handler,
    remove_user_to_exo_hub_handler)

from .user_organization import (
    user_organization_role_post_save,
    user_organization_role_post_delete)


def setup_signals():
    UserProjectRole = apps.get_model(
        app_label='relation', model_name='UserProjectRole',
    )
    ConsultantProjectRole = apps.get_model(
        app_label='relation', model_name='ConsultantProjectRole',
    )
    ConsultantRole = apps.get_model(
        app_label='relation', model_name='ConsultantRole',
    )
    UserProjectRole = apps.get_model(
        app_label='relation', model_name='UserProjectRole',
    )
    ConsultantActivity = apps.get_model(
        app_label='relation', model_name='ConsultantActivity',
    )
    HubUser = apps.get_model(
        app_label='relation', model_name='HubUser',
    )
    OrganizationUserRole = apps.get_model(
        app_label='relation', model_name='OrganizationUserRole',
    )
    Project = apps.get_model(
        app_label='project', model_name='Project')

    # ##
    # UserProjectRole signals
    # ##
    post_save.connect(user_project_role_post_save, sender=UserProjectRole)
    post_delete.connect(user_project_role_post_delete, sender=UserProjectRole)

    # ##
    # ConsultantProjectRole signals
    # ##
    post_save.connect(consultant_project_role_post_save, sender=ConsultantProjectRole)
    post_delete.connect(consultant_project_role_post_delete, sender=ConsultantProjectRole)

    signal_head_coach_created.connect(add_head_coach_project)
    signal_head_coach_removed.connect(remove_head_coach_project)
    signal_add_exo_consultant_role.connect(add_exo_consultant_to_project_handler)
    # ##
    # All user and consultant
    # ##
    signal_user_assigned.connect(all_user_project_when_added)
    signal_user_unassigned.connect(all_user_project_when_removed)
    project_category_changed_signal.connect(
        update_visible_roles, sender=Project)
    pre_save.connect(
        update_visible_project_role, sender=ConsultantProjectRole)
    pre_save.connect(
        update_visible_project_role, sender=UserProjectRole)
    # ##
    # ConsultantActivity Signals
    # ##
    post_save.connect(
        activate_deactivate_consultant_exo_activity_status,
        sender=ConsultantActivity,
    )
    post_save.connect(
        activate_exo_activity_with_no_agreement,
        sender=ConsultantActivity,
    )

    # ##
    # HubUser Signals
    # ##
    post_save.connect(
        hub_user_post_save_handler,
        sender=HubUser,
    )
    post_delete.connect(
        hub_user_post_delete_handler,
        sender=HubUser)

    add_user_exo_hub.connect(
        add_user_to_exo_hub_handler)
    remove_user_exo_hub.connect(
        remove_user_to_exo_hub_handler)

    # InternalOrganizationUser signals

    post_save.connect(
        user_organization_role_post_save, sender=OrganizationUserRole)
    post_delete.connect(
        user_organization_role_post_delete, sender=OrganizationUserRole)

    post_save.connect(
        consultant_role_post_save, sender=ConsultantRole)
    post_delete.connect(
        consultant_role_post_delete, sender=ConsultantRole)

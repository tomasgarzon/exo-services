from django.conf import settings

from invitation.models.mixins.invitation_model_mixin import InvitationModelMixin
from project.models.mixins import ProjectCreationMixin


EXO_ROLE_STRING_KEY_MAPPING = {
    'head_coachs': settings.EXO_ROLE_CODE_SPRINT_HEAD_COACH,
    'speakers': settings.EXO_ROLE_CODE_AWAKE_SPEAKER,
    'coaches': settings.EXO_ROLE_CODE_SPRINT_COACH,
    'align_trainers': settings.EXO_ROLE_CODE_ALIGN_TRAINER,
    'disruptors': settings.EXO_ROLE_CODE_DISRUPTOR,
}


class CustomerProjectMixin(ProjectCreationMixin, InvitationModelMixin):

    def create_generic_project(self, user_from, name, customer, duration, lapse):
        generic_project = self.projects.create_generic_project(
            user_from=user_from,
            name=name,
            customer=self,
            duration=duration,
            lapse=lapse,
        )

        return generic_project

    def create_sprint_automated(self, user_from, name, description, *args, **kwargs):
        self.can_add_service_sprint_automated(user_from)
        sprint_automated = self.projects.create_sprint_automated(
            user_from=user_from,
            name=name,
            description=description,
            customer=self,
            duration=kwargs.get('duration', None),
        )

        return sprint_automated

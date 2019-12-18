from project.managers.project import ProjectManager
from project.models.mixins import ProjectCreationMixin
from custom_auth.helpers import UserProfileWrapper


class FastrackSprintManager(
        ProjectManager,
        ProjectCreationMixin
):
    use_for_related_fields = True
    use_in_migrations = True

    def create_sprint(self, **kwargs):
        user_from = kwargs.pop('user_from')
        self.can_add_service(user_from)
        steps_default = self.model.get_steps()
        if 'duration' not in kwargs:
            kwargs['duration'] = steps_default.get('steps')
        if 'lapse' not in kwargs:
            kwargs['lapse'] = steps_default.get('lapse')
        partner = kwargs.pop('partner')
        kwargs['created_by'] = user_from
        kwargs['internal_organization'] = UserProfileWrapper(user_from).organization
        fastrack = super().create(**kwargs)
        if partner:
            fastrack.project_ptr.partner = partner
        return fastrack

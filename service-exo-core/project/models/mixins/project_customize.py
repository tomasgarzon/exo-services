from django.conf import settings

from exo_role.models import ExORole

from ..project_setting import ProjectSettings


class ProjectCustomize:

    def get_roles(self):
        return {
            'manager': [
                settings.EXO_ROLE_CODE_SPRINT_HEAD_COACH,
            ],
            'team_manager': [
                settings.EXO_ROLE_CODE_SPRINT_COACH,
            ],
            'consultant': [
                settings.EXO_ROLE_CODE_SPRINT_HEAD_COACH,
                settings.EXO_ROLE_CODE_SPRINT_COACH,
            ],
            'labels': [
                self.get_role_label_tuple(settings.EXO_ROLE_CODE_SPRINT_HEAD_COACH),
                self.get_role_label_tuple(settings.EXO_ROLE_CODE_SPRINT_COACH),
            ],
            'multiplicity': [],
        }

    def get_role_label_tuple(self, code):
        return (code, ExORole.objects.get(code=code).__str__())

    @classmethod
    def get_steps(cls, **kwargs):
        return {
            'lapse': None,
            'steps': 0,
            'data': {'name': 'Step %s'},
            'populate': True,
        }

    @classmethod
    def get_roles_can_access_forum(cls):
        return {
            'consultant': [],
            'user': []
        }

    def get_manager_permissions(self):
        return {
            'customer': [
                settings.CUSTOMER_ADD_USER,
                settings.CUSTOMER_EDIT_CUSTOMER,
            ],
            'organization': [],
            'users': [settings.EXO_ACCOUNTS_PERMS_USER_EDIT]
        }

    @property
    def customize(self):
        project_customize = {}
        project_customize['roles'] = self.real_type.get_roles()
        project_customize['steps'] = self.real_type.__class__.get_steps(
            version_2=self.is_version_2)
        project_customize['manager'] = self.get_manager_permissions()
        project_customize['forum'] = self.real_type.__class__.get_roles_can_access_forum()
        return project_customize

    @property
    def customize_roles(self):
        return self.real_type.get_roles()

    @property
    def customize_manager(self):
        return self.get_manager_permissions()

    def role_is_manager(self, exo_role):
        roles = self.customize_roles
        manager_roles = roles.get('manager')
        return exo_role.code in manager_roles

    def role_is_team_manager(self, exo_role):
        roles = self.customize_roles
        manager_roles = roles.get('team_manager')
        return exo_role.code in manager_roles

    @property
    def settings(self):
        try:
            return ProjectSettings.objects.get(project=self)
        except ProjectSettings.DoesNotExist:
            return ProjectSettings.objects.create(
                project=self,
                participant_step_feedback_enabled=self.is_sprint,
                version=settings.PROJECT_CH_VERSION_DEFAULT,
            )

    @property
    def team_manager_label(self):
        labels = [
            dict(self.customize.get('roles').get('labels')).get(code)
            for code in self.customize.get('roles').get('team_manager')
        ]
        return '/'.join(labels)

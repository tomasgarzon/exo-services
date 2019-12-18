from django.conf import settings

from project.models import Project

from .role import ExORoleQuerySet


class ProjectUserQuerySet(ExORoleQuerySet):
    def filter_by_project(self, project):
        return self.filter(project=project)

    def projects(self):
        project_ids = self.values_list('project_id', flat=True)
        return Project.objects.filter(id__in=project_ids)

    def type_normal(self):
        return self.filter(project__customer__customer_type=settings.CUSTOMER_CH_NORMAL)

    def filter_by_user_project_supervisors(self):
        return self.filter_by_exo_role_code(settings.EXO_ROLE_CODE_SPRINT_OBSERVER)

    def filter_by_user_project_members(self):
        return self.filter_by_exo_role_code(settings.EXO_ROLE_CODE_SPRINT_PARTICIPANT)

    def filter_by_user_project_staffs(self):
        return self.filter_by_exo_role_code(settings.EXO_ROLE_CODE_SPRINT_OTHER)

    def filter_by_user_project_delivery_managers(self):
        return self.filter_by_exo_role_code(settings.EXO_ROLE_CODE_DELIVERY_MANAGER)

    def filter_by_user(self, user):
        return self.filter(user=user)

    def exclude_roles(self, roles):
        return self.exclude(exo_role__code__in=roles)

    def exclude_staff(self):
        return self.exclude(exo_role__code=settings.EXO_ROLE_CODE_SPRINT_OTHER)

    def exclude_observer(self):
        return self.exclude(exo_role__code=settings.EXO_ROLE_CODE_SPRINT_OBSERVER)

    def exclude_member(self):
        return self.exclude(exo_role__code=settings.EXO_ROLE_CODE_SPRINT_PARTICIPANT)

    def exclude_staff_and_admin(self):
        roles_code = [
            settings.EXO_ROLE_CODE_SPRINT_OTHER,
            settings.EXO_ROLE_CODE_DELIVERY_MANAGER,
        ]
        return self.exclude_roles(roles_code)

    def exclude_draft_projects(self):
        return self.exclude(project__status=settings.PROJECT_CH_PROJECT_STATUS_DRAFT)

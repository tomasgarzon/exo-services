from django.conf import settings

from utils.permissions.level_mixin import LevelMixin


class ProjectPermissions(LevelMixin):

    def refresh_permissions_for_user(self, user):
        user_levels = {key: 0 for key, _ in settings.PROJECT_ROLE_LEVEL}

        for user_role in user.user_project_roles.filter(project_role__project=self).actives_only():
            for level in user_role.project_role.level:
                user_levels[level] += 1

        self.clear_user_perms(user)
        for key, value in user_levels.items():
            if value > 0:
                self.add_permission(key, user)

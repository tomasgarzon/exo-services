from django.conf import settings


class LevelMixin:

    def user_is_admin(self, user):
        return self.has_permission(
            settings.PROJECT_CH_ROLE_LEVEL_ADMIN,
            user)

    def user_is_basic(self, user):
        return self.has_permission(
            settings.PROJECT_CH_ROLE_LEVEL_BASIC,
            user)

    def user_is_notification(self, user):
        return self.has_permission(
            settings.PROJECT_CH_ROLE_LEVEL_NOTIFICATIONS,
            user)

    def user_is_readonly(self, user):
        return self.has_permission(
            settings.PROJECT_CH_ROLE_LEVEL_READONLY,
            user)

    def users_with_admin_perm(self):
        return self.get_granted_users([settings.PROJECT_CH_ROLE_LEVEL_ADMIN])

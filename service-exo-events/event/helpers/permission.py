from django.contrib.auth import get_user_model
from django.conf import settings


class EventPermissionHelper:

    def _retrieve_data(self, user):
        _, data = get_user_model().objects.retrieve_remote_user_by_uuid(
            user.uuid,
            retrieve_response=True,
        )
        self._user_data = data

    def get_user_certifications(self, user):
        if not hasattr(self, '_user_data'):
            self._retrieve_data(user)
        return self._user_data.get('certifications', [])

    def user_is_consultant(self, user):
        if not hasattr(self, '_user_data'):
            self._retrieve_data(user)
        return self._user_data.get('consultantId') is not None

    def get_events_available(self, user):
        events_availables = []
        if self.user_is_consultant(user):
            user_certifications = self.get_user_certifications(user)
            for type_event in settings.EVENT_PERMMISIONS.keys():
                object_permissions = settings.EVENT_PERMMISIONS.get(type_event)
                if object_permissions:
                    for object_permission in object_permissions:
                        has_specific_permission = any(
                            object_permission in _.get('code')
                            for _ in user_certifications
                        )
                        if len(object_permission) == 0 or has_specific_permission:
                            events_availables.append(type_event)
                else:
                    events_availables.append(type_event)

        if self.can_create_event_summit(user):
            events_availables.append(settings.EXO_ROLE_CATEGORY_SUMMIT)

        return list(set(events_availables))

    def can_create_event_summit(self, user):
        return user.has_perm(settings.EVENT_FULL_PERMS_CREATE_EVENT_SUMMIT)

    def can_publish_event(self, user):
        return user.has_perm(settings.EVENT_FULL_PERMS_MANAGE_EVENT)

    def can_edit_event(self, user, event):
        return user.has_perm(settings.EVENT_PERMS_EDIT_EVENT, event)

    def has_perm(self, user, permission):
        has_perm = True
        if not user.is_superuser:
            type_event = permission.split('_')[1]
            has_perm = type_event in self.get_events_available(user)

            if type_event == settings.EXO_ROLE_CATEGORY_SUMMIT:
                has_perm = self.can_create_event_summit(user)

        return has_perm

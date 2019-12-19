from django.core.exceptions import ValidationError
from django.conf import settings

from ...permission_helpers import (
    user_in_circle, user_can_advise_project_questions,
    user_in_team,
    user_in_qa_session)


class PostPermissionsMixin:

    def can_see(self, user_from, raise_exceptions=True):
        raise NotImplementedError
        if self.is_circle:
            is_valid = self.circle.is_guest_readable or user_in_circle(user_from, self.circle)
        elif self.is_project:
            user_can_advise = user_can_advise_project_questions(user_from)
            user_belongs_to_team = user_in_team(user_from, self.content_object)
            is_valid = user_can_advise or user_belongs_to_team
        elif self.is_q_a_session:
            is_valid = user_in_qa_session(user_from, self.content_object)\
                or user_in_team(user_from, self.content_object.team)
        elif self.is_announcement:
            is_valid = user_from.is_consultant or user_from.is_superuser
        else:
            return False
        if not is_valid and raise_exceptions:
            raise ValidationError("User can't see")
        return is_valid

    def can_reply(self, user_from, raise_exceptions=True):
        raise NotImplementedError
        if self.is_circle:
            is_valid = user_in_circle(user_from, self.content_object)
        elif self.is_project:
            user_can_advise = user_can_advise_project_questions(user_from)
            user_belongs_to_team = user_in_team(user_from, self.content_object)
            is_valid = user_can_advise or user_belongs_to_team
        elif self.is_announcement:
            return user_from.is_consultant or user_from.is_superuser
        elif self.is_q_a_session:
            is_valid = user_in_qa_session(user_from, self.content_object)\
                or user_in_team(user_from, self.content_object.team)
        else:
            return False
        if not is_valid and raise_exceptions:
            raise ValidationError('User can\'t reply')
        return is_valid

    def can_vote(self, user_from, raise_exceptions=True):
        raise NotImplementedError
        if self.is_circle:
            is_valid = user_in_circle(user_from, self.content_object)
        elif self.is_announcement:
            is_valid = user_from.is_consultant or user_from.is_superuser
        else:
            is_valid = self.can_reply(user_from, raise_exceptions)

        if not is_valid and raise_exceptions:
            raise ValidationError('User can\'t vote')
        return is_valid

    def can_rate(self, user_from, raise_exceptions=True):
        raise NotImplementedError
        if self.is_circle or self.is_announcement:
            is_valid = False
        else:
            is_valid = self.can_reply(user_from, raise_exceptions=False)

        if not is_valid and raise_exceptions:
            raise ValidationError('User can\'t rate')
        return is_valid

    def can_update_or_remove(self, user_from, raise_exceptions=True):
        raise NotImplementedError
        is_valid = False

        if self.is_circle or self.is_announcement:
            is_valid = user_from.has_perm(
                settings.FORUM_PERMS_EDIT_POST, self)
        elif self.is_project or self.is_q_a_session:
            user_created_has_perms = user_from.has_perm(
                settings.FORUM_PERMS_EDIT_POST, self)
            if self.is_q_a_session:
                team = self.content_object.team
            else:
                team = self.content_object
            is_valid = user_created_has_perms and user_in_team(user_from, team)
        if not is_valid and raise_exceptions:
            raise ValidationError("User can't update or remove")
        return is_valid

    def can_view_uploaded_file(self, user, raise_exception=True):
        return self.can_see(user, raise_exception)

    def can_upload_files(self, user, raise_exception=True):
        return self.can_update_or_remove(user, raise_exception)

    def can_update_uploaded_file(self, user, uploaded_file_version, raise_exception=True):
        return False

    def can_delete_uploaded_file(self, user, uploaded_file, raise_exception=True):
        return self.can_update_or_remove(user, raise_exception)

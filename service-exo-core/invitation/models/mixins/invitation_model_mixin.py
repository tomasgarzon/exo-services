from django.core.exceptions import ValidationError

from ..invitation import Invitation


class InvitationModelMixin:
    def generate_role_invitation(self, user_from, user_to, role, days=None):
        """Generate an invitation between the user with this role"""
        if user_from is None:
            raise ValidationError("User_from doesn't allow to be null")
        invitation = Invitation.objects.create_role_invitation(
            user_from,
            user_to,
            role,
            days,
        )
        return invitation

    def generate_survey_invitation(self, user_from, user_to, survey, days=None):
        """Generate an invitation for filling a survey"""
        if user_from is None:
            raise ValidationError("User_from doesn't allow to be null")
        invitation = Invitation.objects.create_survey_invitation(
            user_from,
            user_to,
            survey,
            days,
        )
        return invitation

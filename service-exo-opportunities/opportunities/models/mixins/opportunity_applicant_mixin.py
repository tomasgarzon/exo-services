from django.core.exceptions import ValidationError

from auth_uuid.utils.user_wrapper import UserWrapper

from ...conf import settings


class OpportunityApplicantMixin:

    @property
    def advisors_selected(self):
        return self.applicants_selected.users() if self.applicants_selected.exists() else None

    @property
    def applicants_selected(self):
        return self.applicants_info.filter_by_advisor_selected()

    @property
    def applicant_accepted(self):
        return self.applicants_info.filter_by_status_accepted().first()

    def get_or_create_applicant(self, user_from, user):
        return self.applicants_info.get_or_create(
            user=user,
            defaults={
                'status': settings.OPPORTUNITIES_CH_APPLICANT_PENDING,
            },
        )

    def can_apply(self, user_from, raise_exception=True):
        # Return true if user_from can apply for this opportunity
        # user is a consultant
        # user can't apply twice
        if settings.POPULATOR_MODE:
            return True
        user_wrapper = UserWrapper(user=user_from)
        user_is_consultant = user_wrapper.is_consultant

        user_can_apply = user_is_consultant
        opportunity_is_visible = not (self.is_draft or self.is_removed)
        not_applied_yet = not self.get_applicants_for_user(user_from).exists()
        opportunity_can_be_applied = not self.status > settings.OPPORTUNITIES_CH_REQUESTED
        if self.is_opened:
            can_do_action = not_applied_yet and opportunity_can_be_applied
        else:
            user_is_tagged = self.users_tagged.filter(user=user_from).exists()
            can_do_action = not_applied_yet and opportunity_can_be_applied and user_is_tagged

        result = user_can_apply and opportunity_is_visible and can_do_action

        if not result and raise_exception:
            raise ValidationError("User can't apply for this opportunity")

        return result

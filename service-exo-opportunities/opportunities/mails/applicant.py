from django.conf import settings

from auth_uuid.utils.user_wrapper import UserWrapper

from .mixin import OpportunityMailMixin


class ApplicantNotSelected(OpportunityMailMixin):
    def __init__(self, opportunity, user):
        self.user = user
        super().__init__(opportunity)

    def get_data(self):
        data = super().get_data()
        user_wrapper = UserWrapper(user=self.user)
        data.update({
            'applicant_name': user_wrapper.get_full_name(),
            'public_url': settings.OPPORTUNITIES_PUBLIC_URL,
        })
        return data


class ApplicantSelected(OpportunityMailMixin):
    def __init__(self, applicant):
        self.applicant = applicant
        super().__init__(applicant.opportunity)

    def get_data(self):
        data = super().get_data()
        user_wrapper = UserWrapper(user=self.applicant.user)
        file = self.applicant.get_ics_event()
        data.update({
            'applicant_name': user_wrapper.get_full_name(),
            'comment': self.applicant.response_message,
            'public_url': '/ecosystem/opportunities/{}'.format(self.opportunity.pk),
            'opportunity_url': '/ecosystem/opportunities/{}'.format(self.opportunity.pk),
            'start_date_full': self.applicant.start_date_full,
            'attachments': [file] if file else [],
        })
        return data

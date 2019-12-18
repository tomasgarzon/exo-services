from django.conf import settings

from auth_uuid.utils.user_wrapper import UserWrapper

from .mixin import OpportunityMailMixin


class Remove(OpportunityMailMixin):

    def get_data(self):
        data = super().get_data()
        data['public_url'] = settings.OPPORTUNITIES_PUBLIC_URL
        return data


class Edit(OpportunityMailMixin):
    def get_data(self):
        data = super().get_data()
        data['public_url'] = self.opportunity.url_public
        return data


class OpportunityClosed(OpportunityMailMixin):
    def get_data(self):
        data = super().get_data()
        data['public_url'] = self.opportunity.admin_url_public
        return data


class OpportunityCloseReminder(OpportunityMailMixin):
    def get_data(self):
        data = super().get_data()
        data['public_url'] = self.opportunity.admin_url_public
        data['duedate'] = self.opportunity.deadline_date.strftime('%b %d, %H%p')
        return data


class OpportunityFeedback(OpportunityMailMixin):
    def __init__(self, applicant):
        self.applicant = applicant
        super().__init__(applicant.opportunity)

    def get_data(self):
        data = super().get_data()
        user_wrapper = UserWrapper(user=self.applicant.user)
        data.update({
            'applicant_name': user_wrapper.get_full_name(),
        })
        return data

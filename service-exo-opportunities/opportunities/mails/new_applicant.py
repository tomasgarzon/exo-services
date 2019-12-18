from django.conf import settings

from auth_uuid.utils.user_wrapper import UserWrapper

from .mixin import OpportunityMailMixin


class NewApplicant(OpportunityMailMixin):
    def __init__(self, applicant):
        self.applicant = applicant
        super().__init__(applicant.opportunity)

    def get_data(self):
        data = super().get_data()
        user_wrapper = UserWrapper(user=self.applicant.user)
        answers = [
            {
                'question': answer.question.title,
                'response': answer.response,
                'response_text': answer.response_text
            }
            for answer in self.applicant.answers.all()
        ]

        data.update({
            'applicant_profile_picture': user_wrapper.get_profile_picture(settings.LARGE_IMAGE_SIZE),
            'applicant_name': user_wrapper.get_full_name(),
            'applicant_role': user_wrapper.user_title,
            'summary': self.applicant.summary,
            'questions_extra_info': self.applicant.questions_extra_info,
            'applicant_email': user_wrapper.email,
            'applicant_profile_url': user_wrapper.profile_url,
            'public_url': self.opportunity.admin_url_public,
            'answers': answers,
            'reply_to': [
                user_wrapper.email,
            ],

        })
        return data

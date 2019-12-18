import random
from django.conf import settings

from django.utils.translation import ugettext_lazy as _
from utils.faker_factory import faker

from ..mails import BaseMailView


class OpportunityRespondApplicantMailView(BaseMailView):
    template_name = 'mails/opportunity/opportunity_respond_applicant.html'

    mandatory_mail_args = [
        'title',
        'applicant_name',
        'applicant_profile_picture',
        'applicant_role',
        'summary',
        'applicant_email',
        'applicant_profile_url',
        'public_url',
    ]

    subject = _('New opportunity applicant')
    section = 'opportunities'

    def get_mock_data(self, optional=True):
        answers = [
            {
                'question': faker.text(),
                'response': faker.boolean(),
                'response_text': ['Yes', 'No'][random.randint(0, 1)]
            }
            for _ in range(random.randint(0, 2))
        ]
        mock_data = {
            'title': '[Role] for [Project Name]',
            'applicant_name': '[EM Name]',
            'applicant_profile_picture': faker.image_url(settings.DEFAULT_IMAGE_SIZE, settings.DEFAULT_IMAGE_SIZE),
            'applicant_role': '[Applicant User Title]',
            'summary': '[Comment]',
            'questions_extra_info': '[Extra info from Consultant]',
            'applicant_email': '[email]',
            'applicant_profile_url': '/{}'.format(faker.uri_path()),
            'disable_notification_url': None,
            'public_url': '/{}'.format(faker.uri_path()),
            'answers': answers,
        }
        return mock_data

from django.utils.translation import ugettext_lazy as _

from utils.faker_factory import faker

from ..mails import BaseMailView


class SurveyResultUserMailView(BaseMailView):
    """
    """
    template_name = 'mails/survey/result_user.html'

    mandatory_mail_args = [
        'name',
        'survey_name',
        'organization',
        'total',
        'public_url',
        'results',
    ]

    subject = _('ExQ results')
    section = 'exq'

    def get_mock_data(self, optional=True):
        mock_data = {
            'name': '[Name]',
            'survey_name': '[ExQ Name]',
            'organization': '[Organization Name]',
            'total': '[ExQ Value]',
            'disable_notification_url': None,
            'public_url': '/{}'.format(faker.uri_path()),
            'results': [
                {
                    'section': 'M',
                    'section_name': 'Massive Transformative Purpose',
                    'score': '[score]',
                    'max_score': '[max_score]',
                },
                {
                    'section': 'S',
                    'section_name': 'Staff on-demand',
                    'score': '[score]',
                    'max_score': '[max_score]',
                }
            ]
        }
        return mock_data

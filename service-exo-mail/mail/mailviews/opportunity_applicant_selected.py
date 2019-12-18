from django.utils.translation import ugettext_lazy as _

from utils.faker_factory import faker

from ..mails import BaseMailView


class OpportunityApplicantSelectedMailView(BaseMailView):
    template_name = 'mails/opportunity/opportunity_applicant_selected.html'
    mandatory_mail_args = [
        'title',
        'applicant_name',
        'created_by_name',
        'opportunity_url',
        'public_url',
        'start_date_full',
        'category_code',
    ]

    subject = _('Congratulations! The opportunity is yours')
    section = 'opportunities'

    def get_mock_data(self, optional=True):
        mock_data = {
            'title': '[Role] for [Project Name]',
            'applicant_name': '[EM Name]',
            'created_by_name': '[SDM Name]',
            'disable_notification_url': None,
            'response_message': faker.text(),
            'public_url': '/{}'.format(faker.uri_path()),
            'opportunity_url': '/{}'.format(faker.uri_path()),
            'start_date_full': '03 May 2019 12:30 PM (Europe, Madrid)',
            'category_code': 'AC',
        }
        return mock_data

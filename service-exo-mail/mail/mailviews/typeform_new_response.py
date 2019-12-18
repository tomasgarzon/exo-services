# app imports
from django.utils.translation import ugettext_lazy as _

from ..mails import BaseMailView


class NewUserTypeformResponseMailView(BaseMailView):
    template_name = 'mails/typeform/new_response.html'
    mandatory_mail_args = [
        'username',
        'response_related',
        'user_response',
        'public_url',
    ]
    optional_mail_args = []
    subject = _(
        'New response from user %(username)s for %(response_related)s',
    )
    section = 'typeform'

    def get_mock_data(self, optional=True):
        mock_data = super().get_mock_data()
        mock_data.update({
            'username': '[User who complete the typeform]',
            'response_related': '[Response relates to]',
            'user_response': [
                {
                    'id': '1',
                    'title': 'Regular open question',
                    'type': 'short_text',
                    'responses': ['This is my response', ],
                    'options': [],
                },
                {
                    'id': '2',
                    'title': 'Choice questions with one option',
                    'type': 'multiple_choice',
                    'responses': ['Option a', ],
                    'options': ['Option a', 'Option b', 'Option c'],
                },
                {
                    'id': '3',
                    'title': 'Choice question with multiple options',
                    'type': 'multiple_choice',
                    'responses': ['Option a', 'Option c'],
                    'options': ['Option a', 'Option b', 'Option c'],
                },
                {
                    'id': '4',
                    'title': 'True/False question',
                    'type': 'boolean',
                    'responses': ['true'],
                    'options': [],
                },
            ],
            'public_url': 'https://www.google.com',
        })
        return mock_data

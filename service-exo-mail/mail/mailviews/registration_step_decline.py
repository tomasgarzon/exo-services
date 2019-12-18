# app imports
from utils.faker_factory import faker

from ..mails import BaseMailView


class RegistrationStepDeclineMailView(BaseMailView):
    template_name = 'mails/registration/registration_step_decline.html'
    mandatory_mail_args = ['name', 'email', 'step_name']
    optional_mail_args = ['description', 'body_mail']
    subject = '[Registration process] Step declined'
    section = 'registration'

    def get_mock_data(self, optional=True):
        mock_data = {
            'name': faker.first_name(),
            'email': faker.email(),
            'step_name': faker.word(),
        }
        return mock_data

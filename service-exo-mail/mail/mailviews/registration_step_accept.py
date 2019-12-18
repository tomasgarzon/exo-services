# app imports
from utils.faker_factory import faker

from ..mails import BaseMailView


class RegistrationStepAcceptMailView(BaseMailView):
    template_name = 'mails/registration/registration_step_accept.html'
    mandatory_mail_args = ['name', 'email', 'step_name']
    optional_mail_args = ['body_mail']
    section = 'registration'
    subject = '[Registration process] Step accepted'

    def get_mock_data(self, optional=True):
        mock_data = {
            'name': faker.first_name(),
            'email': faker.email(),
            'step_name': faker.word(),
        }
        return mock_data

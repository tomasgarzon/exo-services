from django.conf import settings

from utils.faker_factory import faker

from ..mails import BaseMailView


class WelcomeSimpleUserMailView(BaseMailView):
    template_name = 'mails/user/welcome_simple_user.html'
    section = 'user'
    mandatory_mail_args = [
        'user', 'email',
    ]
    optional_mail_args = []
    subject = 'Your account info at ' + settings.BRAND_NAME

    def get_mock_data(self, optional=True):
        mock_data = {
            'user': faker.first_name(),
            'email': faker.email(),
            'public_url': faker.url()
        }

        return mock_data

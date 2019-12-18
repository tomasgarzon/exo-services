# app imports
from utils.faker_factory import faker

from ..mails import BaseMailView


class NewFeedbackMailView(BaseMailView):
    template_name = 'mails/new_feedback.html'
    mandatory_mail_args = ['name', 'email', 'message']
    optional_mail_args = []
    attachments_args = ['attachment']
    subject = 'A new feedback message has been received'

    def get_mock_data(self, optional=True):
        """Returns mock data for this mail, this will use to preview the html
        or send mock args in the email

        You need to maintain this method if you want better results
        """
        mock_data = {
            'name': faker.first_name(),
            'email': faker.email(),
            'message': faker.sentences(nb=3),
        }
        return mock_data

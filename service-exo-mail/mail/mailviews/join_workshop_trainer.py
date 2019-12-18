from utils.faker_factory import faker

from ..mails import BaseMailView


class JoinWorkshopTrainerMailView(BaseMailView):

    template_name = 'mails/workshop/join_workshop_trainer.html'
    mandatory_mail_args = [
        'workshop_name',
        'location',
        'date',
        'participant_name',
        'participant_email',
        'public_url',
    ]

    subject = 'Attend the Exo Workshop'
    section = 'workshop'

    def get_mock_data(self, option=True):
        return {
            'workshop_name': '[Workshop Name]',
            'location': '[City], [Country]',
            'date': '[dd MM YYYY]',
            'participant_name': '[Attendee Name]',
            'participant_email': '[Attendee Email]',
            'public_url': '/{}'.format(faker.uri_path()),
        }

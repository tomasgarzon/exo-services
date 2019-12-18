from ..mails import BaseMailView


class JoinWorkshopAttendeeMailView(BaseMailView):

    template_name = 'mails/workshop/join_workshop_attendee.html'
    mandatory_mail_args = [
        'workshop_name',
        'location',
        'date'
    ]

    subject = 'Attend the Exo Workshop'
    section = 'workshop'

    def get_mock_data(self, option=True):
        return {
            'workshop_name': '[Workshop Name]',
            'location': '[City], [Country]',
            'date': '[dd MM YYYY]'
        }

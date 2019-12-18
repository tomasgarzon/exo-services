from ..mails import BaseMailView


class EventOwnerNotificationMailView(BaseMailView):
    template_name = 'mails/events/event_owner_notification.html'
    mandatory_mail_args = [
        'event_owner_short_name',
        'event_title',
        'event_type_name',
        'event_date',
        'event_approved',
        'reviewer_user_name',
        'comments',
        'public_url',
    ]
    optional_mail_args = []
    subject = 'Updates for your Event status requested'
    section = 'event'

    def get_mock_data(self, optional=True):
        mock_data = super().get_mock_data()
        mock_data.update({
            'event_owner_short_name': '[Owner short name]',
            'event_title': '[Event Title]',
            'event_type_name': '[Event type name]',
            'event_date': '[Event date]',
            'event_approved': True,
            'reviewer_user_name': '[Reviewer user name]',
            'comments': '[Comments]',
            'public_url': '[Public url]',
        })
        return mock_data

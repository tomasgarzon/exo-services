from ..mails import BaseMailView


class EventManagerNotificationMailView(BaseMailView):
    template_name = 'mails/events/event_manager_notification.html'
    mandatory_mail_args = [
        'event_title',
        'event_type_name',
        'event_date',
        'event_status',
        'event_approved',
        'public_url',
        'user_full_name',
        'user_profile_url',
    ]
    optional_mail_args = []
    subject = 'New event to review'
    section = 'event'

    def get_mock_data(self, optional=True):
        mock_data = super().get_mock_data()
        mock_data.update({
            'event_title': '[Event title]',
            'event_type_name': '[Event type name]',
            'event_date': '[Event date]',
            'event_status': '[Event status]',
            'event_approved': '[Event Approved]',
            'public_url': '[Public URL]',
            'user_full_name': '[Event creator name]',
            'user_profile_url': '[Event creator url]',
        })
        return mock_data

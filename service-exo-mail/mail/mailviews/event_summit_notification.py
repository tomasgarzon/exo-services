from ..mails import BaseMailView


class EventSummitNotificationMailView(BaseMailView):
    template_name = 'mails/events/event_summit_notification.html'
    mandatory_mail_args = [
        'user_full_name',
        'user_profile_url',
        'comments',
    ]
    optional_mail_args = []
    subject = 'New OpenExO Summit request'
    section = 'event'

    def get_mock_data(self, optional=True):
        mock_data = super().get_mock_data()
        mock_data.update({
            'user_full_name': '[User fullname]',
            'user_profile_url': '[User profile url]',
            'comments': '[Comments]',
        })
        return mock_data

from utils.faker_factory import faker


class CircleMixin:
    section = 'circles'

    _mandatory_mail_args = [
        'post_title',
        'public_url',
    ]

    def get_mock_data(self, optional=True):
        mock_data = {
            'public_url': '/{}'.format(faker.uri_path()),
            'post_title': '[Topic title]',
            'disable_notification_url': '/{}'.format(faker.uri_path()),
        }
        return mock_data

    def get_mandatory_mail_args(self):
        args = self._mandatory_mail_args.copy()
        args.extend(self.mandatory_mail_args)
        return args

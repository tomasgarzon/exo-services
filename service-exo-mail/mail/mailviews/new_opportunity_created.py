import random

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from utils.faker_factory import faker

from ..mails import BaseMailView


class NewOpportunityCreatedMailView(BaseMailView):
    template_name = 'mails/opportunity/new_opportunity_created.html'

    mandatory_mail_args = [
        'description',
        'title',
        'created_by_profile_picture',
        'created_by_name',
        'created_by_role',
        'entity_name',
        'location_string',
        'start_date',
        'duration',
        'tags',
        'budget_string',
        'public_url',
        'num_positions'
    ]

    subject = _('New Opportunity')
    section = 'opportunities'

    def get_mock_data(self, optional=True):
        mock_data = {
            'description': '[Description]',
            'title': '[Role] for [Opportunity Title]',
            'created_by_name': '[Created By User]',
            'created_by_profile_picture': faker.image_url(settings.DEFAULT_IMAGE_SIZE, settings.DEFAULT_IMAGE_SIZE),
            'created_by_role': '[User Title]',
            'tags': [faker.word() for _ in range(random.randint(2, 10))],
            'entity_name': '[Entity]',
            'location_string': '[Location]',
            'start_date': '[day] [month], [year]',
            'duration': '[Duration]',
            'budget_string': '[Bugdget]',
            'public_url': '/{}'.format(faker.uri_path()),
            'disable_notification_url': None,
            'num_positions': 33,
        }
        return mock_data

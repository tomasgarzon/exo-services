# app imports
import random

from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from utils.faker_factory import faker

from ..mails import BaseMailView


class InvitationConsultantProjectMailView(BaseMailView):
    template_name = 'mails/invitation_consultant_project.html'
    mandatory_mail_args = [
        'user', 'project_name', 'relation_name',
        'is_coach',
    ]
    optional_mail_args = ['team_name', ]
    subject = _(settings.BRAND_NAME + ' - %(name)s invite')
    section = 'project'

    def get_subject(self, **kwargs):
        is_coach = kwargs.get('is_coach')
        if is_coach:
            return _(settings.BRAND_NAME + ' - Team coach invite')
        else:
            relation_name = kwargs.get('relation_name')
            return self.subject % ({'name': relation_name})

    def get_mock_data(self, optional=True):
        project_name = faker.word()
        team_name = faker.word()
        mock_data = {
            'team_name': team_name,
            'project_name': project_name,
            'relation_name': '[relation_name]',
            'user': faker.first_name(),
            'is_coach': random.randint(0, 1),
            'public_url': '/{}'.format(faker.uri_path()),
        }

        return mock_data

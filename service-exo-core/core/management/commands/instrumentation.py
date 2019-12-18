import json
import subprocess
import requests

from datetime import datetime
from functools import reduce
from rest_framework import status
from requests_toolbelt import MultipartEncoder

from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth import get_user_model

from custom_auth.jwt_helpers import _build_jwt
from forum.models import Post, Answer
from keywords.models import Keyword

from .progress_bar import ProgressBar


class Command(BaseCommand):

    REPORT_FILE_NAME = '_users_{}.csv'
    FILE_HEADER = [
        'User',
        'User Status',
        'Type',
        'Hubs',
        'Certifications',
        'Activities',
        'Roles',
        'Industry',
        'Areas of Expertise',
        'Technology',
        'Language',
        'Country',
        'Last activity',
        'Opps posted',
    ]

    def handle(self, *args, **options):

        self.stdout.write(self.style.WARNING(
            'Generaring instrumentation\n',
        ))
        log = open('{}.log'.format(__file__.split('.py')[0]), 'a')
        report_path = __file__.split('.py')[0]
        report_file_name = self.REPORT_FILE_NAME.format(datetime.now().date(), '%d_%m_%Y')
        report = open('{}{}'.format(report_path, report_file_name), 'w')
        report.write('{}\n'.format('#'.join(self.FILE_HEADER)))

        queryset = get_user_model().objects.all()
        bar = ProgressBar(title='Generating csv file', total=queryset.count())
        for user in queryset:
            bar.step(message=user.email)
            log.write('Logged {} \n'.format(user.email))
            line = '{}#{}#{}#{}#{}#{}#{}#{}#{}#{}#{}#{}#{}#{}'.format(
                user.email,
                'Active' if user.is_active else 'Inactive',
                self.get_user_types(user) or '',
                self.get_user_hubs(user) or '',
                self.get_user_certifications(user) or '',
                self.get_user_activities(user) or '',
                self.get_user_roles(user) or '',
                self.get_user_industries(user) or '',
                self.get_user_expertise(user, 'Expertise') or '',
                self.get_user_expertise(user, 'Technology') or '',
                self.get_user_languages(user) or '',
                user.country or '',
                self.get_user_last_activity(user) or '',
                len(self.get_user_opportunities(user)),
            )

            report.write('{}\n'.format(line))

        report.close()
        log.write('Zipping content ** \n')
        self.zip_file(report_path, report_file_name)

        log.write('Sending email to {} ** \n'.format(settings.INSTRUMENTATION_EMAIL))
        self.send_results_mail(report_path, report_file_name)

        log.write('** Finished **\n')
        log.close()

    def zip_file(self, path, filename):
        subprocess.run([
            'zip',
            '-j',
            '-P',
            settings.ZIPPED_FILES_PASSWORD,
            '{}{}.zip'.format(path, filename),
            '{}{}'.format(path, filename),
        ])

    def get_root(self):
        root = settings.EXOLEVER_HOST + settings.SERVICE_EXO_MAIL_HOST

        return root

    def send_results_mail(self, path, filename):
        url = self.get_root() + 'api/mail/'
        params = {
            'mail_title': 'Instrumentation',
            'mail_content': 'New instrumentation report.',
            'recipients': [settings.INSTRUMENTATION_EMAIL],
        }
        data = {
            'template': 'basic_email',
            'params': params,
            'domain': settings.DOMAIN_NAME,
        }
        fields = data.copy()
        fields['params'] = json.dumps(fields['params'])
        fields.update(
            {'file': (
                '{}.zip'.format(filename),
                open('{}{}.zip'.format(path, filename), 'rb')
            )}
        )
        m = MultipartEncoder(fields=fields)
        requests.post(
            url,
            data=m,
            headers={'Content-Type': m.content_type},
        )

    def get_user_types(self, user):
        types = []
        types.append('Consultant') if user.is_consultant else None
        types.append('Staff') if user.organizations_roles.filter(organization__name=settings.BRAND_NAME).exists() else None  # noqa
        types.append('Client') if user.customers.all().exists() else None
        return ', '.join(types)

    def get_user_hubs(self, user):
        return ', '.join(user.hubs.all().values_list('hub__name', flat=True))

    def get_user_certifications(self, user):
        certifications = []
        if user.is_consultant:
            certifications = [
                user_certification.name
                for user_certification in user.consultant.get_certificates()
            ]

        return ', '.join(certifications)

    def get_user_roles(self, user):
        roles = []
        if user.is_consultant:
            roles = [
                c_project_role.exo_role.name
                for c_project_role in user.consultant.roles.all()
            ]

        return ', '.join(roles)

    def get_user_activities(self, user):
        activities = []
        if user.is_consultant:
            activities = [
                activity.exo_activity.name
                for activity in user.consultant.exo_profile.exo_activities.filter(
                    status=settings.RELATION_ACTIVITY_STATUS_CH_ACTIVE,
                )
            ]

        return ', '.join(activities)

    def get_user_industries(self, user):
        industries = []
        if user.is_consultant:
            industries = user.consultant.industries.values_list(
                'industry__name',
                flat=True,
            )

        return ', '.join(industries)

    def get_user_languages(self, user):
        languages = []
        if user.is_consultant:
            languages = [
                language.name
                for language in user.consultant.languages.all()
            ]

        return ', '.join(languages)

    def get_user_expertise(self, user, type_expertise):
        attributes = []
        if user.is_consultant:
            attrs = list(Keyword.objects.filter(
                tags=type_expertise
            ).order_by('name').values_list('name', flat=True))
            attributes = list(user.consultant.keywords.filter(
                keyword__name__in=attrs
            ).values_list('keyword__name', flat=True))

        return ', '.join(attributes)

    def get_user_last_activity(self, user):
        actitivity_objects = []
        last_activity = None

        last_post = Post.objects.filter(created_by=user).order_by('-modified').first()
        if last_post:
            actitivity_objects.append(
                {'modified': datetime.strftime(last_post.modified, '%Y-%m-%dT%H:%M:%S')}
            )

        last_answer = Answer.objects.filter(created_by=user).order_by('-modified').first()
        if last_answer:
            actitivity_objects.append(
                {'modified': datetime.strftime(last_answer.modified, '%Y-%m-%dT%H:%M:%S')}
            )

        last_opportunity = self.get_last_opportunity(user)
        if last_opportunity:
            actitivity_objects.append(
                {'modified': last_opportunity.get('modified')}
            )

        last_message = self.get_last_user_message(user)
        if last_message:
            actitivity_objects.append(
                {'modified': last_message.get('modified')}
            )

        if actitivity_objects:
            last_activity = reduce(
                compare_dates,
                actitivity_objects,
            ).get('modified')

            last_activity = datetime.strptime(
                last_activity.split('.')[0],
                '%Y-%m-%dT%H:%M:%S',
            )

        return last_activity

    def get_last_user_message(self, user):
        last_message = None
        messages = self.get_user_messages(user)
        if messages:
            last_message = reduce(
                compare_dates,
                messages,
            )

        return last_message

    def get_user_messages(self, user):
        token = _build_jwt(
            get_user_model().objects.get(pk=user.pk))
        headers = {'Authorization': 'Bearer {}'.format(token)}
        url = '{}{}{}'.format(
            settings.EXOLEVER_HOST,
            settings.SERVICE_CONVERSATIONS_HOST,
            'api/{}/messages/'.format(user.uuid),
        )
        response = requests.get(
            url,
            headers=headers
        )
        is_client_error = status.is_client_error(response.status_code)
        is_server_error = status.is_server_error(response.status_code)
        if not is_server_error and not is_client_error:
            return response.json()
        else:
            return []

    def get_last_opportunity(self, user):
        last_opportunity = None
        opportunities = self.get_user_opportunities(user)
        if opportunities:
            last_opportunity = reduce(
                compare_dates,
                opportunities,
            )

        return last_opportunity

    def get_user_opportunities(self, user):
        token = _build_jwt(
            get_user_model().objects.get(pk=user.pk))
        headers = {'Authorization': 'Bearer {}'.format(token)}
        url = '{}{}{}'.format(
            settings.EXOLEVER_HOST,
            settings.SERVICE_EXO_OPPORTUNITIES_HOST,
            'api/opportunity/?only_published_by_you=true',
        )
        response = requests.get(
            url,
            headers=headers
        )

        is_client_error = status.is_client_error(response.status_code)
        is_server_error = status.is_server_error(response.status_code)
        if not is_server_error and not is_client_error:
            return response.json()
        else:
            return []


def compare_dates(a, b):
    if type(a.get('modified')) == str:
        date_a = datetime.strptime(
            a.get('modified').split('.')[0],
            '%Y-%m-%dT%H:%M:%S',
        )
    else:
        date_a = a.get('modified')

    if type(b.get('modified')) == str:
        date_b = datetime.strptime(
            b.get('modified').split('.')[0],
            '%Y-%m-%dT%H:%M:%S',
        )
    else:
        date_b = b.get('modified')

    return a if date_a > date_b else b

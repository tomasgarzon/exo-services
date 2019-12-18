import csv

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings

from consultant.models import Consultant
from project.models import Project
from team.models import Team
from utils.faker_factory import faker
from utils.func_utils import infer_method_name


User = get_user_model()


class Command(BaseCommand):

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('project_id', nargs='+', type=int)
        parser.add_argument('filename', nargs='+', type=str)
        parser.add_argument(
            '--consultants',
            action='store_true',
            dest='consultants',
            help='Import CSV for consultants',
        )

    def handle(self, *args, **options):  # noqa
        project_id = options.get('project_id')[0]
        project = Project.objects.get(pk=project_id)
        if options.get('consultants'):
            filename = options.get('consultants')[0]
            with open(filename, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    rol = row.get('Rol')
                    lista = rol.get('List')
                    for k in lista:
                        consultant = Consultant.objects.filter(user__emailaddress__email=k).get()
                        method_name = infer_method_name(rol, 'get_or_create')
                        method = getattr(project.consultants_roles, method_name)
                        method(
                            user_from=User.objects.filter(is_superuser=True).first(),
                            consultant=consultant,
                            project=project,
                        )
        k_team = project.project_manager.user
        filename = options.get('filename')[0]
        with open(filename, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            team = {}
            last_team_name = ''
            other_data = {}
            for row in reader:
                team_name = row.get('Team')
                if team_name != last_team_name:
                    if last_team_name:
                        teams = Team.objects.filter(project=team['project'], name=team['name'])
                        if teams.exists():
                            team_members = team.get('team_members', [])
                            team = teams[0]
                            for member in team_members:
                                team.add_member(
                                    user_from=team.created_by,
                                    email=member.get('email'),
                                    name=member.get('short_name'),
                                )
                        else:
                            team = Team.objects.create(
                                user_from=User.objects.filter(is_superuser=True).first(),
                                **team
                            )
                        last_team_name = team_name
                    team = {
                        'project': project,
                        'name': team_name,
                        'stream': row.get('Stream'),
                        'created_by': k_team,
                        'coach': Consultant.objects.filter(
                            user__emailaddress__email=row.get('Coach'),
                        ).get(),
                        'team_members': [],
                    }
                full_name = '{} {}'.format(
                    row.get('First Name'), row.get('Last Name'),
                )
                short_name = row.get('First Name')
                user_email = row.get('Email').strip().lower()
                if settings.DEBUG:
                    user_email = faker.email()
                team['team_members'].append({
                    'email': user_email,
                    'short_name': short_name,
                })
                bio = row.get('Bio')
                phone = row.get('Phone')
                other_data[user_email] = {
                    'bio': bio,
                    'phone': phone,
                    'full_name': full_name,
                    'linkedin': row.get('Linkedin')
                }
                last_team_name = row.get('Team')
            teams = Team.objects.filter(project=team['project'], name=team['name'])
            if teams.exists():
                team_members = team.get('team_members', [])
                team = teams[0]
                for member in team_members:
                    team.add_member(
                        user_from=team.created_by,
                        email=member.get('email'),
                        name=member.get('short_name'),
                    )
            else:
                team = Team.objects.create(
                    user_from=User.objects.filter(is_superuser=True).first(),
                    **team
                )

        for email, data in other_data.items():
            user = User.objects.get(email=email)
            user.full_name = data['full_name']
            user.about_me = data['bio']
            user.phone = data['phone']
            if data.get('linkedin'):
                user.linkedin = data.get('linkedin')
            user.save()

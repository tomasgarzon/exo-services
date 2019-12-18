import csv

from django.core.management.base import BaseCommand

from ...models import Consultant


class Command(BaseCommand):
    help = 'Export consultat as csv'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('output', nargs='+', type=str)

    def handle(self, *args, **options):
        self.stdout.write('Export consultant')
        filename = options.get('output')[0]
        header = [
            'Name', 'email', 'Location',
            'Languages', 'Status',
            'Is ExO Certified',
            'ExO Activities', 'ExO Roles',
            'Total Projects', 'Joined',
            'Last Activity'
        ]
        with open(filename, 'w') as filename:
            writer = csv.writer(filename)
            writer.writerow(header)
            for item in Consultant.all_objects.all():
                languages = [language.name for language in item.languages.all()]
                roles = {c_project_role.exo_role.name for c_project_role in item.roles.all()}
                activities = [
                    '{} [{}]'.format(
                        activity.exo_activity.name, activity.get_status_display())
                    for activity in item.exo_profile.exo_activities.all()
                ]

                row = [
                    item.user.full_name,
                    item.user.email,
                    item.user.location,
                    ', '.join(languages),
                    item.status_detail,
                    item.is_exo_certified,
                    ', '.join(activities),
                    ', '.join(list(roles)),
                    item.projects.all().count(),
                    item.user.date_joined,
                    item.user.ecosystem_member.last_activity,
                ]

                writer.writerow(row)
        self.stdout.write('Finish!!')

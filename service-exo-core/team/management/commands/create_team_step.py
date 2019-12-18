from django.core.management.base import BaseCommand

from project.models import Project

from ...models import TeamStep


class Command(BaseCommand):
    help = (
        'Create team-step model for all the current project'
    )

    def handle(self, *args, **options):
        for project in Project.objects.all():
            for team in project.teams.all():
                for step in project.steps.all():
                    TeamStep.objects.get_or_create(step=step, team=team)

        self.stdout.write('\n Finish!! \n\n')

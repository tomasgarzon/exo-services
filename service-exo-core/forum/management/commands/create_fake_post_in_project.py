from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings

from project.models import Project
from utils.faker_factory import faker
from utils.random import random
from consultant.models import Consultant
from keywords.models import Keyword
from exo_activity.models import ExOActivity

from ...models import Post

User = get_user_model()


class Command(BaseCommand):
    help = (
        'Create random post and aswers for each project'
    )

    def handle(self, *args, **options):
        self.stdout.write('\n Creating Questions/Answers for testing: \n\n')
        consultants = Consultant.objects.all()
        exo_consulting = ExOActivity.objects.get(code=settings.EXO_ACTIVITY_CH_ACTIVITY_CONSULTING)
        for project in Project.objects.filter(teams__isnull=False):
            users = User.objects.filter(teams__project=project)
            if not users:
                continue
            self.stdout.write('\n Creating questions for %s' % str(project))
            for i in range(random.randint(2, 10)):
                user = random.choices(users, k=1)[0]
                try:
                    post = Post.objects.create_project_team_post(
                        user_from=user,
                        team=user.teams.filter(project=project).first(),
                        title=' '.join(faker.words()),
                        description=faker.text(),
                        tags=random.choices(
                            Keyword.objects.all(), k=random.randint(2, 6)),
                    )
                except Exception:
                    continue
                for consultant in set(random.choices(consultants, k=random.randint(2, 10))):
                    exo_activity, _ = consultant.exo_profile.exo_activities.get_or_create(
                        exo_activity=exo_consulting)
                    exo_activity.enable()
                    post.see(consultant.user)
                for consultant in set(random.choices(consultants, k=random.randint(2, 10))):
                    exo_activity, _ = consultant.exo_profile.exo_activities.get_or_create(
                        exo_activity=exo_consulting)
                    exo_activity.enable()
                    post.see(consultant.user)
                    post.reply(consultant.user, faker.text())
        self.stdout.write('\n Finish!! \n\n')

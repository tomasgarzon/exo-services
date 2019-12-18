from django.core.management.base import BaseCommand
from django.conf import settings
from django.db.models import Q

from project.models import Project
from qa_session.models import QASession

from ...helpers import update_or_create_badge
from ...project_helpers import create_user_project_role_badge, create_consultant_project_role_badge
from ...models import UserBadge


class Command(BaseCommand):

    def create_swarm_badge(self):
        category = settings.EXO_ROLE_CATEGORY_SWARM
        long_description = 'Initial migration'

        for qa_session in QASession.objects.all():
            title = qa_session.project.name

            for consultant_project_role in qa_session.members.all():
                user = consultant_project_role.consultant.user
                code = settings.EXO_ROLE_CODE_SWARM_ADVISOR
                item = {
                    'name': title,
                    'date': qa_session.start_at.date()
                }
                update_or_create_badge(
                    user_from=user,
                    user_to=user,
                    code=code,
                    category=category,
                    items=[item],
                    description=long_description)

    def create_projects_badge(self):
        q1 = Q(consultants_roles__isnull=True)
        q2 = Q(users_roles__isnull=True)
        queryset = Project.objects.exclude(q1 & q2)

        for item in queryset:
            self.create_project_badge(item)

    def create_project_badge(self, project):
        for consultant_project_role in project.consultants_roles.all().actives_only():
            create_consultant_project_role_badge(consultant_project_role)
        for user_project_role in project.users_roles.all().actives_only():
            create_user_project_role_badge(user_project_role)

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating user badges ...')

        UserBadge.objects.all().exclude(badge__category=settings.BADGE_CATEGORY_COMMUNITY).delete()

        self.create_swarm_badge()
        self.create_projects_badge()
        self.stdout.write(self.style.SUCCESS('User Badges created'))

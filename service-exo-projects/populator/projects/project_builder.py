from populate.populator.builder import Builder

from opportunities.helper import initialize_advisor_request_settings_for_project
from project.models import Project, UserProjectRole
from project.signals_define import project_created_signal


class ProjectBuilder(Builder):

    def create_project_members(self, project):
        members = self.data.get('members', [])
        for member in members:
            project_role = project.project_roles.get(role=member.get('role'))
            UserProjectRole.objects.get_or_create(
                created_by=project.created_by,
                user=member.get('user'),
                project_role=project_role,
                active=member.get('active', True))

    def create_project_participants(self, project):
        members = self.data.get('participants', [])
        for member in members:
            user_project_role = UserProjectRole.objects.create_participant(
                project=project,
                created_by=project.created_by,
                name=member.get('name'),
                email=member.get('email'))
            if member.get('uuid'):
                user = user_project_role.user
                user.uuid = member.get('uuid')
                user.save()
                participant = user.participant
                participant.delete()

    def update_roles(self, project):
        if not project.is_draft:
            for user_role in UserProjectRole.objects.filter(project_role__project=project):
                user_role.activate(project.created_by)

    def create_advisor_settings(self, project):
        advisor_settings = self.data.get('advisor_settings')
        if not project.is_draft:
            initialize_advisor_request_settings_for_project(
                project, project.created_by)
            advisor_request_settings = project.advisor_request_settings
            advisor_request_settings.total = advisor_settings.get('total')
            advisor_request_settings.budgets = advisor_settings.get('budgets', [])
            advisor_request_settings.save()

    def create_object(self):
        project, _ = Project.objects.get_or_create(
            id=self.data.get('id'),
            uuid=self.data.get('uuid'),
            customer=self.data.get('customer', None),
            name=self.data.get('name'),
            content_template=self.data.get('content_template'),
            start=self.data.get('start'),
            end=self.data.get('end'),
            location=self.data.get('place').get('name'),
            place_id=self.data.get('place').get('place_id'),
            status=self.data.get('status'),
            created_by=self.data.get('created_by'),
        )
        project_created_signal.send(
            sender=project.__class__,
            project=project)
        self.create_project_members(project)
        self.create_project_participants(project)
        self.update_roles(project)
        self.create_advisor_settings(project)
        project.teams.all().delete()
        return project

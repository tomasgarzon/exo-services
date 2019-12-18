from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import parsers

from utils.mail import handlers
from project.views.mixin import ProjectPermissionMixin

from ..serializers.email import TeamEmailSerializer
from ...models import Team


class SendMessageView(ProjectPermissionMixin, APIView):
    serializer_class = TeamEmailSerializer
    parser_classes = (parsers.MultiPartParser, )
    project_permission_required = settings.PROJECT_PERMS_PROJECT_MANAGER

    def post(self, request, project_id, format=None):
        serializer = self.serializer_class(data=request.data, context=self)
        serializer.is_valid(raise_exception=True)
        project = self.get_project()
        attachments = request.FILES.getlist('attachments[]')
        try:
            role = project.consultants_roles.filter_by_user(request.user)[0]
            role_name = role.label
        except IndexError:
            role_name = ''
        for team_data in serializer.validated_data.get('teams'):
            team = Team.objects.get(pk=team_data.get('id'))
            for user in team.team_members.all():
                handlers.mail_handler.send_mail(
                    'email_team',
                    recipients=[user.email],
                    reply_to=[request.user.email],
                    from_email=request.user.email,
                    subject_args={'subject': serializer.validated_data.get('subject')},
                    message=serializer.validated_data.get('message'),
                    role_name=role_name,
                    project_name=self.get_project().name,
                    name=request.user.short_name,
                    subject=serializer.validated_data.get('subject'),
                    public_url=project.get_frontend_index_url(user),
                    attachments=attachments,
                )
        return Response({'status': 'ok'})

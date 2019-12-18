from rest_framework.views import APIView
from rest_framework import renderers
from rest_framework.permissions import IsAuthenticated
from djangorestframework_camel_case.render import CamelCaseJSONRenderer
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser

from django.conf import settings

from ...models import Project
from utils.drf.parsers import CamelCaseJSONParser


class JoinUserCertificationLevel1(APIView):
    model = Project
    permission_classes = (IsAuthenticated, )
    parser_classes = (CamelCaseJSONParser, MultiPartParser)
    renderer_classes = (CamelCaseJSONRenderer, renderers.JSONRenderer, )

    def post(self, request, language='en'):
        user = request.user
        data = {'nextURL': settings.DOMAIN_NAME}
        project_id = settings.PROJECT_CERTIFICATION_LEVEL_1_LANGUAGE.get(language)

        try:
            project = self.model.objects.get(pk=project_id)
        except Exception:
            project = None
        if project:
            team = project.teams.first()
            team.add_member(
                user_from=project.created_by,
                email=user.email,
                name=user.short_name,
            )
            data['nextURL'] += project.get_frontend_index_url(user)
        return Response(data)

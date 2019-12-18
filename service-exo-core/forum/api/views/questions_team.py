from django.shortcuts import get_object_or_404

from djangorestframework_camel_case.render import CamelCaseJSONRenderer
from utils.drf.parsers import CamelCaseJSONParser
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from permissions.objects import get_team_for_user
from project.models import Project

from ..serializers.mixins import BasicPageNumberPagination
from ..serializers import answer, ask, post


class QuestionsTeamViewSet(viewsets.ModelViewSet):
    renderer_classes = (CamelCaseJSONRenderer, )
    parser_classes = (CamelCaseJSONParser,)
    permission_classes = (IsAuthenticated, )
    pagination_class = BasicPageNumberPagination
    serializers = {
        'default': post.PostListSerializer,
        'retrieve': post.PostDetailSerializer,
        'create': ask.AskTheEcosystemSerializer,
        'answers': answer.AnswerPostSerializer,
    }
    swagger_schema = None

    def get_queryset(self):
        project = get_object_or_404(Project, pk=self.kwargs.get('project_pk'))
        team = get_team_for_user(
            project, self.request.user
        ).get(pk=self.kwargs.get('team_pk'))
        queryset = team.posts.all()
        search = self.request.GET.get('search', '')
        return queryset.filter_by_search(search)

    def get_serializer_class(self):
        return self.serializers.get(
            self.action,
            self.serializers['default'],
        )

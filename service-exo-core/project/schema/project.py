from django.urls import reverse
from django.conf import settings

import graphene
from graphene import AbstractType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphene.types.json import JSONString

from utils.schema import CustomNode
from files.schema import ResourceNode, ResourceFilterSet
from team.schema import TeamNode
from permissions.shortcuts import has_project_perms

from .filters import TeamFilter, ProjectFilter, PublicProjectFilter
from .public_project import PublicProjectNode
from ..models import Project
from ..helpers import next_project_url
from ..api.serializers.project_settings import ProjectSettingsSerializer


class ProjectNode(DjangoObjectType):
    uuid = graphene.String()
    first_day = graphene.String()
    last_day = graphene.String()
    timezone = graphene.String()
    type_project = graphene.String()
    lapse_type = graphene.String()
    project_incidences = JSONString()
    resources = DjangoFilterConnectionField(
        ResourceNode,
        filterset_class=ResourceFilterSet)
    count_resources = graphene.Int()
    my_teams = DjangoFilterConnectionField(TeamNode, filterset_class=TeamFilter)
    teams = DjangoFilterConnectionField(TeamNode, filterset_class=TeamFilter)
    next_url = JSONString()
    admin_url = graphene.String()
    allowed_access = graphene.Boolean()
    settings = JSONString()
    has_swarm_session = graphene.Boolean()

    class Meta:
        model = Project
        interfaces = (CustomNode, )
        filter_fields = ['name', 'status']

    def resolve_timezone(self, info):
        return self.timezone.zone if self.timezone else None

    def resolve_my_teams(self, info, **kwargs):
        queryset = self.teams \
            .filter_by_project(self) \
            .filter_by_user(self, info.context.user)

        filter = TeamFilter(queryset=queryset, **kwargs)
        return filter.queryset

    def resolve_teams(self, info, **kwargs):
        queryset = self.teams.filter_by_project(self)
        filter = TeamFilter(queryset=queryset, **kwargs)
        return filter.queryset

    def resolve_count_resources(self, info):
        return self.resources.count()

    def resolve_next_url(self, info):
        url, zone = next_project_url(self, info.context.user)
        return {'url': url, 'zone': zone}

    def resolve_admin_url(self, info):
        url = ''
        if has_project_perms(
            self,
            settings.PROJECT_PERMS_PROJECT_MANAGER,
            info.context.user,
        ):
            url = reverse('project:project:dashboard', kwargs={'project_id': self.pk})

        return url

    def resolve_project_incidences(self, info):
        project_incidences = {}
        type_incidence = None
        number_incidences = 0

        if has_project_perms(
            self,
            settings.PROJECT_PERMS_PROJECT_MANAGER,
            info.context.user,
        ):
            errors_incidences = self.validations \
                .filter_by_validation_type_error() \
                .filter_by_status_pending().count()
            warnings_incidences = self.validations \
                .filter_by_validation_type_warning() \
                .filter_by_status_pending().count()

            if errors_incidences:
                type_incidence = self.validations \
                    .filter_by_validation_type_error() \
                    .first().validation_type
                number_incidences = errors_incidences

            elif warnings_incidences:
                type_incidence = self.validations \
                    .filter_by_validation_type_warning() \
                    .first().validation_type
                number_incidences = warnings_incidences

            project_incidences = {'type': type_incidence, 'number': number_incidences}

        return project_incidences

    def resolve_allowed_access(self, info):
        return self.real_type.allowed_access

    def resolve_type_project(self, info):
        return self.type_verbose_name

    def resolve_settings(self, info):
        return ProjectSettingsSerializer(self.settings).data

    def resolve_has_swarm_session(self, info):
        return self.qa_sessions.exists()


class Query(AbstractType):
    all_project = DjangoFilterConnectionField(
        ProjectNode,
        filterset_class=ProjectFilter,
    )

    def resolve_all_project(self, info, **kwargs):
        # info.context will reference to the Django request
        if not info.context.user.is_authenticated:
            queryset = Project.objects.none()
        else:
            queryset = Project.objects.filter_by_user_or_organization(info.context.user).order_by('-start')
        return queryset.filter(**kwargs)


class PublicQuery(AbstractType):
    all_project = DjangoFilterConnectionField(
        PublicProjectNode,
        filterset_class=PublicProjectFilter,
    )

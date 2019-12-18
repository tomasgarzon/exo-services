from graphene_django import DjangoObjectType
import graphene
from graphene_django.filter import DjangoFilterConnectionField

from utils.schema import CustomNode
from custom_auth.schema import UserNode, UserFilter
from project.schema import StepNode
from project.schema.filters import StepFilterSet

from .models import Team


class TeamNode(DjangoObjectType):
    stream_display = graphene.String()
    zoom_url = graphene.String()
    group_uuid = graphene.String()
    team_members = DjangoFilterConnectionField(
        UserNode,
        filterset_class=UserFilter)
    steps = DjangoFilterConnectionField(
        StepNode,
        filterset_class=StepFilterSet)

    class Meta:
        model = Team
        interfaces = (CustomNode, )

    def resolve_stream_display(self, info):
        return self.get_stream_display()

    def resolve_zoom_url(self, info):
        return self.zoom_url(info.context.user)

    def resolve_team_members(self, info):
        return self.team_members.all()

    def resolve_steps(self, info):
        return self.project.steps.all()

    def resolve_group_uuid(self, info):
        try:
            return self.opportunity_group.group_uuid
        except AttributeError:
            return None

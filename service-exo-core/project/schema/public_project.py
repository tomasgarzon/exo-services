from graphene import relay
import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from ..models import Project
from .public_step import PublicStepNode
from .filters import StepFilterSet


class PublicProjectNode(DjangoObjectType):
    first_day = graphene.String()
    last_day = graphene.String()
    timezone = graphene.String()
    lapse_type = graphene.String()
    steps = DjangoFilterConnectionField(
        PublicStepNode,
        filterset_class=StepFilterSet)

    class Meta:
        model = Project
        interfaces = (relay.Node, )
        only_fields = ['agenda']

    def resolve_timezone(self, info):
        return self.timezone.zone if self.timezone else None

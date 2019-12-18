from graphene_django import DjangoObjectType
import graphene
from graphene_django.filter import DjangoFilterConnectionField

from relation.schema.consultant_exo_activity import ConsultantExOActivityNode, ConsultantActivityFilterSet
from utils.schema import CustomNode

from ..models import ConsultantExOProfile, ContractingData


class ConsultantExOProfileNode(DjangoObjectType):
    _mtp_mastery = graphene.Int()
    areas_expertise = graphene.List(graphene.Int)
    wanted_roles = graphene.List(graphene.Int)
    exo_activities = DjangoFilterConnectionField(
        ConsultantExOActivityNode,
        filterset_class=ConsultantActivityFilterSet)

    class Meta:
        model = ConsultantExOProfile
        interfaces = (CustomNode, )

    def resolve__mtp_mastery(self, info):
        # Redefine level field, because there is a bug in graphehe.
        # when integer field has choices, it transforms 4 to A_4 as value.
        return self.mtp_mastery

    def resolve_exo_activities(self, info):
        return self.exo_activities.all()


class ContractingAreaNode(DjangoObjectType):

    class Meta:
        model = ContractingData
        interfaces = (CustomNode, )

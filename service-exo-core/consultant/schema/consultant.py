import graphene

from django.db.models import F, Max

from graphene import AbstractType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from relation.schema import ConsultantIndustryNode, ConsultantIndustryFilterSet
from utils.schema import CustomNode, Connection
from core.schema import LanguageNode, LanguageFilterSet

from ..models import Consultant, ConsultantValidationStatus

from .filters import AllConsultantFilter, ConsultantFilter


class ConsultantValidationStatusNode(DjangoObjectType):
    class Meta:
        model = ConsultantValidationStatus
        interfaces = (CustomNode, )


class ConsultantNode(DjangoObjectType):
    max_industries = DjangoFilterConnectionField(
        ConsultantIndustryNode,
        filterset_class=ConsultantIndustryFilterSet)
    languages = DjangoFilterConnectionField(
        LanguageNode,
        filterset_class=LanguageFilterSet)
    video_url = graphene.String()

    class Meta:
        model = Consultant
        interfaces = (CustomNode, )
        connection_class = Connection

    def resolve_max_industries(self, info, **kwargs):
        industries = self.industries.annotate(
            max_level=Max('consultant__industries__level'),
        ).filter(level=F('max_level'))
        return industries

    def resolve_video_url(self, info, **kwargs):
        return self.exo_profile.video_url


class Query(AbstractType):
    consultant = CustomNode.Field(ConsultantNode)
    all_consultants = DjangoFilterConnectionField(
        ConsultantNode,
        filterset_class=AllConsultantFilter,
    )
    active_consultants = DjangoFilterConnectionField(
        ConsultantNode,
        filterset_class=ConsultantFilter,
    )

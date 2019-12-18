from graphene_django import DjangoObjectType
import graphene
import django_filters
from utils.schema import CustomNode

from ..models import ConsultantIndustry


class ConsultantIndustryFilterSet(django_filters.FilterSet):
    pk = django_filters.CharFilter()

    class Meta:
        model = ConsultantIndustry
        fields = ['pk']


class ConsultantIndustryNode(DjangoObjectType):
    _level = graphene.Int()
    level_description = graphene.String()

    class Meta:
        model = ConsultantIndustry
        interfaces = (CustomNode, )

    def resolve__level(self, info):
        # Redefine level field, because there is a bug in graphehe.
        # when integer field has choices, it transforms 4 to A_4 as value.
        return self.level

    def resolve_level_description(self, info):
        return self.get_level_display()

from graphene_django import DjangoObjectType
from graphene import AbstractType
from graphene_django.filter import DjangoFilterConnectionField
import graphene
import django_filters

from utils.schema import CustomNode

from .models import ExOArea


class ExOAreaFilterSet(django_filters.FilterSet):
    pk = django_filters.CharFilter()

    class Meta:
        model = ExOArea
        fields = ['pk']


class ExOAreaNode(DjangoObjectType):
    code = graphene.String()

    class Meta:
        model = ExOArea
        interfaces = (CustomNode, )

    def resolve_code(self, info):
        return self.code


class Query(AbstractType):
    all_exo_areas = DjangoFilterConnectionField(
        ExOAreaNode,
        filterset_class=ExOAreaFilterSet
    )

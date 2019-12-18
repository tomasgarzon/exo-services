from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphene import AbstractType
import django_filters
from utils.schema import CustomNode

from .models import ExOHub


class ExOHubFilterSet(django_filters.FilterSet):
    pk = django_filters.CharFilter()

    class Meta:
        model = ExOHub
        fields = ['pk']


class ExOHubNode(DjangoObjectType):

    class Meta:
        model = ExOHub
        interfaces = (CustomNode, )


class Query(AbstractType):
    all_hubs = DjangoFilterConnectionField(
        ExOHubNode,
        filterset_class=ExOHubFilterSet,
    )

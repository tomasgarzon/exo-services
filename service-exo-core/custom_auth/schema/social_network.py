from graphene_django import DjangoObjectType
import django_filters
from utils.schema import CustomNode

from exo_accounts.models import SocialNetwork


class SocialNetworkFilterSet(django_filters.FilterSet):
    pk = django_filters.CharFilter()

    class Meta:
        model = SocialNetwork
        fields = ['pk']


class SocialNetworkNode(DjangoObjectType):
    class Meta:
        model = SocialNetwork
        interfaces = (CustomNode, )

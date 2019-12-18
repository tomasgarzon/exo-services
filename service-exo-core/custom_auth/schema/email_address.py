from graphene_django import DjangoObjectType
import django_filters
from utils.schema import CustomNode

from exo_accounts.models import EmailAddress


class EmailAddressFilterSet(django_filters.FilterSet):
    pk = django_filters.CharFilter()

    class Meta:
        model = EmailAddress
        fields = ['pk']


class EmailAddressNode(DjangoObjectType):
    class Meta:
        model = EmailAddress
        interfaces = (CustomNode, )

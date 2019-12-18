import django_filters
from graphene import relay, AbstractType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from utils.schema import CustomNode

from ..models import Customer


class CustomerFilter(django_filters.FilterSet):
    partner = django_filters.CharFilter(method='filter_by_partner')
    no_partner = django_filters.BooleanFilter(method='filter_no_partner')

    class Meta:
        model = Customer
        fields = {
            'name': ['exact', 'icontains', 'istartswith'],
            'partner': [],
            'no_partner': [],
        }

    def filter_by_partner(self, queryset, name, value):
        return queryset.filter_by_partner(value)

    def filter_no_partner(self, queryset, name, value):
        if value:
            return queryset.filter_no_partners()
        return queryset


class CustomerNode(DjangoObjectType):

    class Meta:
        model = Customer
        interfaces = (CustomNode, )
        exclude_fields = ['timezone']


class Query(AbstractType):

    customer = relay.Node.Field(CustomerNode)
    all_customers = DjangoFilterConnectionField(
        CustomerNode,
        filterset_class=CustomerFilter,
        description='All customers',
    )

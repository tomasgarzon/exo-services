from graphene import relay, AbstractType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from utils.schema import CustomNode

from .models import Partner


class PartnerNode(DjangoObjectType):

    class Meta:
        model = Partner
        interfaces = (CustomNode, )
        filter_fields = {
            'name': ['exact', 'icontains', 'istartswith'],
        }


class Query(AbstractType):

    partner = relay.Node.Field(PartnerNode)
    all_partners = DjangoFilterConnectionField(
        PartnerNode,
        description='All partners',
    )

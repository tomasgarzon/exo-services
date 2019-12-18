from graphene import relay
from graphene_django import DjangoObjectType

from ..models import Step


class PublicStepNode(DjangoObjectType):

    class Meta:
        model = Step
        interfaces = (relay.Node, )
        only_fields = ['start', 'end']

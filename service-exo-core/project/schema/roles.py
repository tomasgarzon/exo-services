from graphene import relay
from graphene_django import DjangoObjectType

from exo_role.models import ExORole


class ExORoleNode(DjangoObjectType):

    class Meta:
        model = ExORole
        interfaces = (relay.Node, )

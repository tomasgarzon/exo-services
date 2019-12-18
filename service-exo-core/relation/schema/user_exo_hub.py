from graphene_django import DjangoObjectType

from utils.schema import CustomNode

from ..models import HubUser


class HubUserNode(DjangoObjectType):

    class Meta:
        model = HubUser
        interfaces = (CustomNode, )

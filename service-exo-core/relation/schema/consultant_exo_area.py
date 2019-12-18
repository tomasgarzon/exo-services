from graphene_django import DjangoObjectType

from utils.schema import CustomNode

from ..models import ConsultantExOArea


class ConsultantExOAreaNode(DjangoObjectType):
    class Meta:
        model = ConsultantExOArea
        interfaces = (CustomNode, )

from graphene_django import DjangoObjectType

from utils.schema import CustomNode

from .models import Industry


class IndustryNode(DjangoObjectType):
    class Meta:
        model = Industry
        interfaces = (CustomNode, )

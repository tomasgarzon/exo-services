from graphene_django import DjangoObjectType

from utils.schema import CustomNode

from .models import ExOAttribute


class ExOAttributeNode(DjangoObjectType):
    class Meta:
        model = ExOAttribute
        interfaces = (CustomNode, )

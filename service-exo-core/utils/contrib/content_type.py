from django.contrib.contenttypes.models import ContentType

from graphene_django import DjangoObjectType

from utils.schema import CustomNode


class ContentTypeNode(DjangoObjectType):
    class Meta:
        model = ContentType
        interfaces = (CustomNode, )

import graphene
from graphene_django import DjangoObjectType

from utils.schema import CustomNode

from ..models import UploadedFile, UploadedFileVersion


class UploadedFileVersionNode(DjangoObjectType):

    version = graphene.Int()
    url = graphene.String()

    class Meta:
        model = UploadedFileVersion
        interfaces = (CustomNode,)
        only_fields = ('version', 'url', )


class UploadedFileNode(DjangoObjectType):
    """How to include in other Graphql Nodes:"""
    version = graphene.Int()
    url = graphene.String()

    class Meta:
        model = UploadedFile
        interfaces = (CustomNode, )

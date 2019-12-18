import graphene

from graphene_django import DjangoObjectType

from utils.schema import CustomNode

from ..models import UserMicroLearning


class UserMicroLearningNode(DjangoObjectType):

    typeform_url = graphene.String()

    class Meta:
        model = UserMicroLearning
        interfaces = (CustomNode, )

    def resolve_typeform_url(self, info):
        return self.typeform_url

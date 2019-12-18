from graphene_django import DjangoObjectType
import graphene

from utils.schema import CustomNode

from ..models import ConsultantKeyword


class ConsultantKeywordNode(DjangoObjectType):
    _level = graphene.Int()
    level_description = graphene.String()

    class Meta:
        model = ConsultantKeyword
        interfaces = (CustomNode, )

    def resolve__level(self, info):
        # Redefine level field, because there is a bug in graphehe.
        # when integer field has choices, it transforms 4 to A_4 as value.
        return self.level

    def resolve_level_description(self, info):
        return self.get_level_display()

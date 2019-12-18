from graphene_django import DjangoObjectType
import django_filters
from graphene_django.filter import DjangoFilterConnectionField

from utils.schema import CustomNode

from .models import Keyword


class TagKeywordNode(DjangoObjectType):

    class Meta:
        model = Keyword.tags.tag_model
        interfaces = (CustomNode,)


class TagKeywordFilterSet(django_filters.FilterSet):
    pk = django_filters.CharFilter()

    class Meta:
        model = Keyword.tags.tag_model
        fields = ['pk']


class KeywordFilterSet(django_filters.FilterSet):
    pk = django_filters.CharFilter()

    class Meta:
        model = Keyword
        fields = ['pk']


class KeywordNode(DjangoObjectType):
    tags = DjangoFilterConnectionField(
        TagKeywordNode,
        filterset_class=TagKeywordFilterSet)

    class Meta:
        model = Keyword
        interfaces = (CustomNode, )

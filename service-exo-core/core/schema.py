from graphene_django import DjangoObjectType
import django_filters

from utils.schema import CustomNode

from .models import Language


class LanguageFilterSet(django_filters.FilterSet):
    pk = django_filters.CharFilter()

    class Meta:
        model = Language
        fields = ['pk']


class LanguageNode(DjangoObjectType):
    class Meta:
        model = Language
        interfaces = (CustomNode, )

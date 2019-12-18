from graphene import relay
import graphene
import guardian
import django_filters
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from django.contrib.contenttypes.models import ContentType


class ContentTypeFilterSet(django_filters.FilterSet):
    pk = django_filters.CharFilter()

    class Meta:
        model = ContentType
        fields = ['pk']


class GenericContentTypeNode(DjangoObjectType):
    pk = graphene.ID()

    class Meta:
        model = ContentType
        interfaces = (relay.Node, )

    def resolve_pk(self, context, info):
        return self.pk


class CustomNode(relay.Node):
    pk = graphene.ID()
    content_type_id = graphene.ID()
    content_type = DjangoFilterConnectionField(
        GenericContentTypeNode,
        filterset_class=ContentTypeFilterSet)
    permissions = graphene.List(graphene.String)

    class Meta:
        name = 'CustomNode'

    def resolve_pk(self, info):
        return self.pk

    def resolve_content_type_id(self, info):
        return ContentType.objects.get_for_model(self).pk

    def resolve_content_type(self, info):
        return [ContentType.objects.get_for_model(self)]

    def resolve_permissions(self, info):
        return guardian.shortcuts.get_user_perms(info.context.user, self)


class Connection(graphene.Connection):
    total_count = graphene.Int()

    class Meta:
        abstract = True

    def resolve_total_count(self, info):
        return self.length

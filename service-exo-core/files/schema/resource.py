from graphene_django import DjangoObjectType
import graphene
from sizefield.utils import filesizeformat
from graphql.language.ast import Variable
import django_filters
from utils.schema import CustomNode

from ..models import Resource


class TagResourceNode(DjangoObjectType):

    class Meta:
        model = Resource.tags.tag_model
        interfaces = (CustomNode,)


class ResourceFilterSet(django_filters.FilterSet):
    pk = django_filters.CharFilter()

    class Meta:
        model = Resource
        fields = ['pk']


class ResourceNode(DjangoObjectType):
    is_link = graphene.Boolean()
    is_file = graphene.Boolean()
    type = graphene.String()
    url = graphene.String()
    file_name = graphene.String()
    public_tags = graphene.List(graphene.String)
    file_size = graphene.String()

    class Meta:
        model = Resource
        interfaces = (CustomNode, )

    def resolve_file_size(self, info):
        if self.file_size:
            return filesizeformat(self.file_size)
        return None

    def resolve_public_tags(self, info):
        # search project in the grahql query
        public_tags = None
        op_name = info.operation.selection_set.selections[0].name
        if op_name.value == 'allProject':
            project_id = None
            for argument in info.operation.selection_set.selections[0].arguments:
                if argument.name.value == 'pk':
                    if isinstance(argument.value, Variable):
                        project_id = info.variable_values.get(argument.name.value)
                    else:
                        project_id = argument.value.value
                    break
            if project_id:
                self._project = project_id
                public_tags = self.public_tags
        return public_tags

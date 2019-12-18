import django_filters

from django.db.models import Q

from ...models import Resource
from .resource_filter_mixin import ResourceFilterMixin


class ResourceSectionsFilter(django_filters.FilterSet):
    sections = django_filters.CharFilter(field_name='sections', method='filter_sections')

    def filter_sections(self, queryset, name, value):
        query = Q()
        values = self.get_filter_values(value)

        for value in values:
            query |= Q(sections__icontains=value)

        return queryset.filter(query)


class ResourceProjectsFilter(django_filters.FilterSet):
    projects = django_filters.CharFilter(field_name='projects', method='filter_projects')

    def filter_projects(self, queryset, name, value):
        projects = self.get_filter_values(value)
        query = Q()
        for project in projects:
            query |= Q(projects__contains=project)
        return queryset.filter(query)


class ResourceFilter(ResourceFilterMixin, ResourceSectionsFilter):

    class Meta:
        model = Resource
        fields = ['name', 'tags', 'status', 'sections']


class ResourceProjectFilter(ResourceFilterMixin, ResourceProjectsFilter):

    class Meta:
        model = Resource
        fields = ['name', 'tags', 'status', 'projects']

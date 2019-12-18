import django_filters

from team.models import Team

from ..models import Project, Step


class TeamFilter(django_filters.FilterSet):
    pk = django_filters.CharFilter()

    class Meta:
        model = Team
        fields = {
            'name': ['exact', 'icontains'],
        }


class ProjectFilter(django_filters.FilterSet):
    # Do case-insensitive lookups on 'name'
    status = django_filters.CharFilter(lookup_expr='iexact')
    pk = django_filters.CharFilter()

    class Meta:
        model = Project
        fields = ['status', 'name', 'customer__name', 'pk']


class PublicProjectFilter(django_filters.FilterSet):
    class Meta:
        model = Project
        fields = ['slug', 'name']


class StepFilterSet(django_filters.FilterSet):
    pk = django_filters.CharFilter()

    class Meta:
        model = Step
        fields = ['pk']

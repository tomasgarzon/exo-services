from django.conf import settings
from django.db.models import Q

from django_filters import rest_framework as filters

from ...models import Event


class EventFilterSet(filters.FilterSet):

    category = filters.MultipleChoiceFilter(
        method='filter_category',
        label='Category',
        choices=settings.EVENT_TYPE_CHOICES,
    )
    follow_type = filters.MultipleChoiceFilter(
        method='filter_follow_type',
        label='Follow Type',
        choices=settings.EVENT_FOLLOW_MODE_CHOICES,
    )

    languages = filters.CharFilter(
        method='filter_languages',
    )

    location = filters.CharFilter(
        method='filter_location',
    )

    class Meta:
        model = Event
        fields = [
            'category',
            'follow_type',
            'languages',
            'location'
        ]

    def filter_category(self, queryset, name, value):
        query = Q()
        for query_value in value:
            query |= Q(category__code=query_value)
        return queryset.filter(query)

    def filter_follow_type(self, queryset, name, value):
        query = Q()
        for query_value in value:
            query |= Q(follow_type__contains=query_value)
        return queryset.filter(query)

    def filter_languages(self, queryset, name, value):
        query = Q()
        for language in value.split(','):
            query |= Q(languages__contains=[language])
        return queryset.filter(query)

    def filter_location(self, queryset, name, value):
        query = Q()
        for location in value.split(','):
            query |= Q(location__icontains=location)

        return queryset.filter(query)

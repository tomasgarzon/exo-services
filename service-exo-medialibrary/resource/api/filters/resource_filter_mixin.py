import django_filters

from ...models import Resource, Category, Tag


class ResourceFilterMixin(django_filters.FilterSet):
    tags = django_filters.CharFilter(field_name='tags', method='filter_tags')
    status = django_filters.CharFilter()

    def filter_tags(self, queryset, name, value):
        categories = self.get_categories_set(value)
        tags = self.get_tags_set(value, categories)
        queryset = queryset.filter(tags__slug__in=tags) if tags else queryset
        queryset = queryset.filter(tags__category__slug__in=categories) if categories else queryset
        return queryset

    def get_filter_values(self, value):
        values_array = value.split(',')
        return [item for item in values_array if item]

    def get_categories_set(self, value):
        filter_list_values = self.get_filter_values(value)
        return set(Category.objects.all().values_list('slug', flat=True)).intersection(set(filter_list_values))

    def get_tags_set(self, value, exclude_categories):
        filter_list_values = self.get_filter_values(value)
        return set(Tag.objects.all().exclude(slug__in=list(exclude_categories)).values_list(
            'slug', flat=True)).intersection(set(filter_list_values))

    class Meta:
        model = Resource
        fields = ['name', 'tags', 'status']

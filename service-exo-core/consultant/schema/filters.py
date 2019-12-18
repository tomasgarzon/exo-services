import django_filters

from django.db.models import Q

from ..models import Consultant


class AllConsultantFilter(django_filters.FilterSet):
    # Do case-insensitive lookups on 'name'
    status = django_filters.CharFilter(lookup_expr='iexact')
    user__email = django_filters.CharFilter(field_name='user__email')
    user__short_name = django_filters.CharFilter(field_name='user__short_name')
    pk = django_filters.CharFilter()

    class Meta:
        model = Consultant
        fields = ['status', 'user__email', 'user__short_name', 'pk']

    @property
    def qs(self):
        self.queryset = self._meta.model.all_objects.all()
        return super().qs


class ConsultantFilter(django_filters.FilterSet):
    content = django_filters.CharFilter(method='my_content_filter')

    class Meta:
        model = Consultant
        fields = ['content']

    def my_content_filter(self, queryset, name, value):
        query = {'user__short_name__icontains': value}
        query['user__full_name__icontains'] = value
        query['user__location__icontains'] = value
        query_final = Q()
        for k1, k2 in query.items():
            q2 = {k1: k2}
            query_final |= Q(**q2)
        return queryset.filter(query_final)

from django.db.models import Max


class UniqueOrderMixin():

    def create_unique(self, name_field, *args, **kwargs):
        query_kwargs = kwargs

        queryset = self._meta.default_manager.filter(
            **query_kwargs
        ).aggregate(Max(name_field))

        max_order = 1
        if queryset.get('order__max'):
            max_order = queryset.get('order__max') + 1
        else:
            max_order = 1
        return max_order

from django.db.models import Q, QuerySet


class QuerySetFilterComplexMixin(QuerySet):
    _fields_from_form = {}
    _split_by = ' '

    def filter_complex(self, *args, **kwargs):
        query_final = Q()
        queries = []
        for key, value in kwargs.items():
            if not value:
                continue
            query_field = self._fields_from_form.get(key)
            if isinstance(query_field, list):
                query = Q()
                for q1 in query_field:
                    for v1 in value.split(self._split_by):
                        data = {q1: v1}
                        query |= Q(**data)
            else:
                # dynamic function filter_by_FOO
                if getattr(self, 'filter_by_' + key, None):
                    query = getattr(self, 'filter_by_' + key)(value)
                else:
                    query = Q()
                    if isinstance(value, str):
                        for v1 in value.split(self._split_by):
                            data = {query_field: v1}
                            query |= Q(**data)
                    else:
                        data = {query_field: value}
                        query = Q(**data)
            queries.append(query)
        for query in queries:
            query_final &= query
        return self.filter(query_final).distinct()

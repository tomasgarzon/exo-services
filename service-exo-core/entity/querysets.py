from utils.queryset import QuerySetFilterComplexMixin


class EntityQuerysetMixin(QuerySetFilterComplexMixin):

    _fields_from_form = {
        'search': [
            'name__icontains',
            'industry__name__icontains',
        ],
    }

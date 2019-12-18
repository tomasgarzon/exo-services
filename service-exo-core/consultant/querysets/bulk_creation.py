from utils.queryset import QuerySetFilterComplexMixin


class BulkCreationQueryset(QuerySetFilterComplexMixin):

    _fields_from_form = {
        'search': [
            'created_by__short_name__icontains',
            'file_csv__icontains',
        ],
    }

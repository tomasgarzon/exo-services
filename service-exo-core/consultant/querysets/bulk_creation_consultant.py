from utils.queryset import QuerySetFilterComplexMixin


class BulkCreationConsultantQueryset(QuerySetFilterComplexMixin):

    _fields_from_form = {
        'search': [
            'name__icontains',
            'email__icontains',
            'status__icontains',
        ],
    }

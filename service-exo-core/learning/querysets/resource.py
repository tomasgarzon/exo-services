from utils.queryset import QuerySetFilterComplexMixin


class ResourceQuerySet(QuerySetFilterComplexMixin):
    _fields_from_form = {
        'search': [
            'name__icontains',
            'description__icontains',
            'tags__name__icontains',
        ],
    }

    def actives(self):
        return self.filter(active=True)

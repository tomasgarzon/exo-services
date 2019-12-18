class UniqueNameMixin:
    _suffix = '_'

    def generate_suffix(self, suffix, number):
        if suffix == self._suffix:
            return suffix * number
        else:
            return str(suffix % (number + 1))

    def create_unique(self, value, name_field, suffix, *args, **kwargs):
        value_query = value
        counter = 1
        query_kwargs = kwargs
        query_kwargs[name_field] = value_query
        while self._meta.default_manager.filter(**query_kwargs).exclude(id=self.id).exists():
            new_suffix = self.generate_suffix(suffix, counter)
            value_query = value + new_suffix
            counter += 1
            query_kwargs[name_field] = value_query
        return value_query

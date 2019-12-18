class CurrentProjectDefault:
    def set_context(self, serializer_field):
        self.project = serializer_field.context['view'].project

    def __call__(self):
        return self.project

    def __repr__(self):
        return '%s()' % self.__class__.__name__

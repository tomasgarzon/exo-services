class CurrentTeamDefault:
    def set_context(self, serializer_field):
        self.team = serializer_field.context['view'].team

    def __call__(self):
        return self.team

    def __repr__(self):
        return '%s()' % self.__class__.__name__

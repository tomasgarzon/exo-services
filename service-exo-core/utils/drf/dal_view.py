from dal import autocomplete


class DALAutocomplete(autocomplete.Select2QuerySetView):

    def has_add_permission(self, request):
        """Return True if the user has the permission to add a model."""
        return request.user.is_authenticated

    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return self.model.objects.none()

        qs = self.model.objects.all()
        if self.q:
            qs = qs.filter(name__istartswith=self.q)
        return qs

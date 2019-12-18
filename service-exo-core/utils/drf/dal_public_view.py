from dal import autocomplete


class DALAutocompleteSelect2Public(autocomplete.Select2QuerySetView):
    """
        DALAutocomplete open for public access (Survey cumplimentation)
    """

    def get_queryset(self):
        qs = self.model.objects.all()
        if self.q:
            qs = qs.filter(name__istartswith=self.q)
        return qs


class AutocompleteSelect2Mixin(autocomplete.Select2QuerySetView):

    # Redefine this because a Bug at DAL
    def post(self, request, *args, **kwargs):
        return super().post(request)

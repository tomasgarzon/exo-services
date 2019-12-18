from django.shortcuts import get_object_or_404


class APIObjectMixin:
    """
    This API is for DRF Open api doc package
    Some views crash when pk is requested in lookup_field
    We manage this case in order to see api details in docs
    """

    def get_object(self, *args, **kwargs):

        queryset = self.filter_queryset(self.get_queryset())
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        try:
            filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
            obj = get_object_or_404(queryset, **filter_kwargs)
            self.check_object_permissions(self.request, obj)
        except KeyError:
            obj = None

        return obj

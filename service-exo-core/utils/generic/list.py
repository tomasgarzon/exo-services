from django.views.generic.list import ListView
from .bulk_form import BulkActionsForm


class ListFilterView(ListView):
    filter_form_class = None
    bulk_action_list = None

    def get(self, request, *args, **kwargs):
        execute_call = False

        self.form_filter = self.filter_form_class(request.GET)
        method_to_call = request.GET.get('actions', None)

        self.form_bulk = None
        if self.bulk_action_list:
            for action, name in self.bulk_action_list:
                if not hasattr(self, action):
                    raise NotImplementedError
                if method_to_call == action:
                    execute_call = True

            self.form_bulk = BulkActionsForm(
                queryset=self.get_queryset(),
                options=self.bulk_action_list,
            )

        if execute_call:
            params = request.GET.get('object_list', None)
            return getattr(self, method_to_call)(params)

        return super().get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['form_filter'] = self.form_filter
        context['form_bulk'] = self.form_bulk
        context['object_class'] = context.get('object_list').model._meta.model_name

        return context

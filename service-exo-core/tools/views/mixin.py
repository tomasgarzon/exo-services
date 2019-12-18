from braces.views import GroupRequiredMixin

from ..conf import settings


class ToolPermissionMixin(GroupRequiredMixin):
    """

    """
    _group_required = settings.TOOLS_GROUP_NAME

    def get_group_required(self):
        # Get group or groups however you wish
        group = [self._group_required]
        if getattr(self, 'tool_group_required', None):
            group.append(self.tool_group_required)
        return group


class ToolsQuerySetListView(object):

    def get_queryset(self, queryset=None):
        if not queryset:
            queryset = self.model.objects.all()
        self.form_filter.is_valid()
        data = self.form_filter.cleaned_data
        queryset = queryset.filter_complex(*data, **data)
        return queryset.distinct()

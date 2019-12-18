from project.queryset.project import BaseProjectQuerySet


class StepQuerySet(BaseProjectQuerySet):
    _fields_from_form = {
        'search': [
            'streams__goal__icontains',
            'streams__guidelines__icontains',
        ],
    }

    def filter_by_project(self, project):
        return self.filter(project=project)

    def filter_by_sprint(self, sprint):
        return self.filter_by_project(project=sprint.project_ptr)

    def filter_by_lapse(self, lapse):
        return self.filter(project__lapse=lapse)

    def filter_by_index_range(self, start, end):
        return self.filter(index__gte=start, index__lte=end)

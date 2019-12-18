class ProjectQuerySetMixin(object):
    """
        QuerySet Mixin to add filter_by_project method to queryset
    """

    def filter_by_project(self, project):
        return self.filter(project=project)

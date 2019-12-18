class AssignmentsMixin:

    def populate_assignments_version_2(self, project, template):
        project.update_assignments_template(template)

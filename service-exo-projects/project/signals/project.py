from ..tasks import ProjectPopulateTask, AssignResourcesToProjectTask
from ..models import Step


def post_created_project(sender, project, *args, **kwargs):
    ProjectPopulateTask().s(
        project_id=project.pk).apply_async()
    AssignResourcesToProjectTask().s(
        project_id=project.pk).apply_async()


def project_start_changed_handler(sender, instance, *args, **kwargs):
    Step.objects.start_steps(instance)

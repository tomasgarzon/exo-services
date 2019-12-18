from ..tasks import (
    ProjectJobCreate,
    ProjectJobUpdate,
    ProjectJobDelete,
    ProjectOpportunityJobUpdate,
)


def post_job_save_handler(sender, instance, created, *args, **kwargs):
    if created:
        try:
            instance.user_project_role.opportunity_related
            ProjectOpportunityJobUpdate().s(
                job_id=instance.id).apply_async()
        except AttributeError:
            ProjectJobCreate().s(job_id=instance.id).apply_async()
    else:
        ProjectJobUpdate().s(job_id=instance.id).apply_async()


def post_job_delete_handler(sender, instance, *args, **kwargs):
    ProjectJobDelete().s(job_uuid=instance.uuid.__str__()).apply_async()


def change_user_role_handler(sender, instance, *args, **kwargs):

    for user_project_role in instance.user.user_project_roles.filter(job__isnull=False):
        job = user_project_role.job
        ProjectJobUpdate().s(job_id=job.id).apply_async()

from ..tasks import (
    JobCreate,
    JobUpdate,
    JobDelete,
    EventOpportunityJobUpdate,
)


def post_job_save_handler(sender, instance, created, *args, **kwargs):
    if created:
        try:
            instance.participant.opportunity_related
            EventOpportunityJobUpdate().s(
                job_id=instance.id).apply_async()
        except AttributeError:
            JobCreate().s(job_id=instance.id).apply_async()
    else:
        JobUpdate().s(job_id=instance.id).apply_async()


def post_job_delete_handler(sender, instance, *args, **kwargs):
    JobDelete().s(job_uuid=instance.uuid.__str__()).apply_async()

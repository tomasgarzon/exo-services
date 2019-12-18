from ..tasks import (
    ApplicantJobCreate, ApplicantJobUpdate, ApplicantJobDelete)


def post_job_save_handler(sender, instance, created, *args, **kwargs):
    if created:
        ApplicantJobCreate().s(job_id=instance.id).apply_async()
    else:
        ApplicantJobUpdate().s(job_id=instance.id).apply_async()


def post_job_delete_handler(sender, instance, *args, **kwargs):
    ApplicantJobDelete().s(job_uuid=instance.uuid.__str__()).apply_async()

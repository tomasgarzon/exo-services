from ..models import CoreJob
from ..tasks import CoreJobCreate, CoreJobUpdate, CoreJobDelete


def create_core_job(instance, created=False):
    if instance.need_job:
        if created:
            CoreJob.objects.create_from_instance(instance)
        else:
            core_jobs = CoreJob.objects.all().filter_by_instance(instance)

            if core_jobs.exists():
                for core_job in core_jobs:
                    CoreJobUpdate().s(job_id=core_job.id).apply_async()
            else:
                CoreJob.objects.create_from_instance(instance)
    else:
        CoreJob.objects.all().filter_by_instance(instance).delete()


def core_job_post_save(sender, instance, created, *args, **kwargs):
    if created:
        CoreJobCreate().s(job_id=instance.id).apply_async()


def core_job_post_delete(sender, instance, *args, **kwargs):
    CoreJobDelete().s(uuid=instance.uuid.__str__()).apply_async()


def job_instance_post_save(sender, instance, created, *args, **kwargs):
    create_core_job(instance, created)


def job_instance_post_delete(sender, instance, *args, **kwargs):
    CoreJob.objects.all().filter_by_instance(instance).delete()


def related_instance_post_update(sender, instance, created, *args, **kwargs):
    instance.update_related_jobs()


def related_instance_post_delete(sender, instance, *args, **kwargs):
    instance.delete_related_jobs()

from ..models import Job


def create_job_handler(sender, instance, *args, **kwargs):
    if instance.active:
        Job.objects.update_or_create(user_project_role=instance)
    elif hasattr(instance, 'job'):
        Job.objects.filter(user_project_role=instance).delete()

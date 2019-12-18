from django.db.models.signals import post_save

from jobs.signals_define import create_job


def post_applicant_sow_save_handler(sender, instance, created, *args, **kwargs):
    applicant = instance.applicant
    if created or not hasattr(applicant, 'job'):
        create_job.send(
            applicant=applicant,
            sender=applicant.__class__)
    else:
        post_save.send(
            instance=applicant.job,
            created=False,
            sender=applicant.job.__class__)


def post_applicant_sow_delete_handler(sender, instance, *args, **kwargs):
    applicant = instance.applicant

    if hasattr(applicant, 'job'):
        applicant.job.delete()

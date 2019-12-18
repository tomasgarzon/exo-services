from ..models import Job


def create_job_handler(sender, applicant, *args, **kwargs):
    Job.objects.create(applicant=applicant)

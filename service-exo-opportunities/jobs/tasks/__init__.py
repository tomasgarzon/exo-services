from service.celery import app

from .applicant import ApplicantJobCreate, ApplicantJobUpdate, ApplicantJobDelete


app.tasks.register(ApplicantJobCreate())
app.tasks.register(ApplicantJobUpdate())
app.tasks.register(ApplicantJobDelete())

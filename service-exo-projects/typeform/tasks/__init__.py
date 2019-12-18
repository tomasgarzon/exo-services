from celery import current_app as app

from .typeform_feedback import UpdateUserGenericTypeformFeedbackTask

app.tasks.register(UpdateUserGenericTypeformFeedbackTask())

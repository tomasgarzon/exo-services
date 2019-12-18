from celery import current_app as app

from .typeform_feedback import UpdateUserGenericTypeformFeedbackTask
from .service_mail import SendMailTask


app.tasks.register(UpdateUserGenericTypeformFeedbackTask())
app.tasks.register(SendMailTask())

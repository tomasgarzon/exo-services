from service.celery import app
from .send_email import SendMailTask

app.tasks.register(SendMailTask())

from service.celery import app

from .webhook_first_message import WebhookOpportunityFirstMessageTask


app.tasks.register(WebhookOpportunityFirstMessageTask())

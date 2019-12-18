from celery import current_app as app

from .hubspot import HubspotCertificationDealSyncTask, HubspotCertificationDealDeleteTask


app.tasks.register(HubspotCertificationDealSyncTask())
app.tasks.register(HubspotCertificationDealDeleteTask())

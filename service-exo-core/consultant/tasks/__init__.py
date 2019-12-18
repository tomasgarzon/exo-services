from celery import current_app as app

from .hubspot_integrations import (
    CreateHubspotContactTask,
    HubspotContactConvertToMemberTask,
    HubspotContactAddCertificationTask,
    HubspotUpdateContactEmailTask,
    HubspotUpdateContactFoundationsDate,
)
from .consultant import NetworkListReportTask, ContractingDataListReportTask
from .certification import CertificationReportTask


app.tasks.register(CreateHubspotContactTask())
app.tasks.register(HubspotContactConvertToMemberTask())
app.tasks.register(HubspotContactAddCertificationTask())
app.tasks.register(NetworkListReportTask())
app.tasks.register(ContractingDataListReportTask())
app.tasks.register(HubspotUpdateContactEmailTask())
app.tasks.register(CertificationReportTask())
app.tasks.register(HubspotUpdateContactFoundationsDate())

from django.conf import settings

from ..tasks import HubspotCertificationDealDeleteTask


def certification_deletion_handler(sender, instance, **kwargs):
    if not settings.POPULATOR_MODE:
        HubspotCertificationDealDeleteTask().s(
            certification_pk=instance.pk,
            deal_pk=instance.hubspot_deal,
        )

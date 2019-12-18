import logging

from django.conf import settings
from django.core.management import call_command
from django.db.models import Q

from ..models import CertificationRequest
from ..tasks import HubspotCertificationDealSyncTask


logger = logging.getLogger('service')


def certification_request_status_updated_handler(sender, pk, **kwargs):
    if not settings.POPULATOR_MODE:
        HubspotCertificationDealSyncTask().s(pk=pk).apply_async()


def certification_request_post_save_handler(sender, instance, created, **kwargs):
    if not created and not settings.POPULATOR_MODE:
        call_command('synchronize_certification_deal', '--pk={}'.format(instance.pk))


def certification_request_issue_certification(sender, user, course_name, credential, **kwargs):
    certification_role = credential.content_object.certification_role
    certification_request = None

    cert_filter = Q(
        certification__certification_role=certification_role,
        user=user,
        status=settings.EXO_CERTIFICATION_REQUEST_STATUS_CH_APPROVED,
    )

    try:
        certification_request = CertificationRequest.objects.get(cert_filter)
    except CertificationRequest.DoesNotExist:
        return
    except CertificationRequest.MultipleObjectsReturned as exc:
        certification_request.CertificationRequest.objects.filter(cert_filter).first()
        logger.error('Signal.certification_request_issue_certification: {}'.format(exc))

    if certification_request:
        certification_request.status = settings.EXO_CERTIFICATION_REQUEST_STATUS_CH_FINISHED
        certification_request.save(update_fields=['status'])

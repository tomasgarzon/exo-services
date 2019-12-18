from django.conf import settings

from utils.segment import SegmentAnalytics
from ..models import CertificationRequest, ExOCertification

FOUNDATIONS = 'Foundations'


def certification_request_acquired_handler(sender, user, consultant_role, *args, **kwargs):
    certification_requests = CertificationRequest.objects.filter(
        user=user,
        status=settings.EXO_CERTIFICATION_REQUEST_STATUS_CH_APPROVED,
        certification__certification_role=consultant_role.certification_role,
    )

    certification = None

    if certification_requests.exists():
        certification_request = certification_requests.first()
        certification_request.acquire_certificate(consultant_role)
        certification = certification_request.certification

    if not certification:
        certification = ExOCertification.objects.get(
            level=settings.EXO_CERTIFICATION_CERTIFICATION_CH_LEVEL_1)

    category = settings.EXO_CERTIFICATION_INSTRUMENTATION_EVENTS.get(
        certification.level)
    data = {
        'user': user,
        'category': category,
        'event': settings.INSTRUMENTATION_EVENT_CERTIFICATION_SENT,
    }

    if certification.level != settings.EXO_CERTIFICATION_CERTIFICATION_CH_LEVEL_1:
        data['certificationType'] = certification.get_level_display()

    SegmentAnalytics.event(**data)

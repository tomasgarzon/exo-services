from django.conf import settings

from exo_certification.models import ExOCertification, CertificationRequest
from project.helpers import next_project_url


CERTIFICATION_REQUIRED = 'R'


def construct_exo_certification_request(user):
    project = None
    exo_certification_request = None
    has_requested_exo_foundation = None
    has_exo_foundation_certification = user.consultant.certification_roles.filter(
        code=settings.EXO_ROLE_CODE_CERTIFICATION_FOUNDATIONS,
    ).exists()
    has_consultant_certification = user.consultant.certification_roles.filter(
        code=settings.EXO_ROLE_CODE_CERTIFICATION_CONSULTANT,
    ).exists()

    exo_foundation_status = ''
    if has_exo_foundation_certification:
        exo_foundation_status = settings.EXO_CERTIFICATION_REQUEST_STATUS_CH_FINISHED
    else:
        has_requested_exo_foundation = user.projects_member.filter(
            project__pk__in=settings.PROJECT_CERTIFICATION_LEVEL_1,
        ).exists()
        has_requested_certification_level_2 = user.certification_request.filter(
            certification__level=settings.EXO_CERTIFICATION_CERTIFICATION_CH_LEVEL_2,
        ).exists()

        if (has_requested_certification_level_2 or has_consultant_certification) and not has_requested_exo_foundation:
            exo_foundation_status = CERTIFICATION_REQUIRED
        elif has_requested_exo_foundation:
            exo_foundation_status = settings.EXO_CERTIFICATION_REQUEST_STATUS_CH_PENDING

    if has_exo_foundation_certification or has_requested_exo_foundation or has_requested_certification_level_2:
        exo_certification_request = CertificationRequest(
            user=user,
            certification=ExOCertification.objects.get(
                level=settings.EXO_CERTIFICATION_CERTIFICATION_CH_LEVEL_1,
            ),
            status=exo_foundation_status,
        )
        if has_requested_exo_foundation:
            project = user.projects_member.filter(
                project__pk__in=settings.PROJECT_CERTIFICATION_LEVEL_1,
            ).first().project

        if project:
            url, _ = next_project_url(project, user)
            exo_certification_request.url_foundations = url

    return exo_certification_request

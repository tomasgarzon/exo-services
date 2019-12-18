from django.conf import settings
from exo_role.models import CertificationRole

from .models import Circle


CERTIFIED_CIRCLE_SLUGS = {
    settings.CIRCLES_SLUG_AMBASSADORS: settings.EXO_ROLE_CODE_CERTIFICATION_AMBASSADOR,
    settings.CIRCLES_SLUG_COACHES: settings.EXO_ROLE_CODE_CERTIFICATION_SPRINT_COACH,
    settings.CIRCLES_SLUG_CONSULTANTS: settings.EXO_ROLE_CODE_CERTIFICATION_CONSULTANT,
    settings.CIRCLES_SLUG_TRAINERS: settings.EXO_ROLE_CODE_CERTIFICATION_TRAINER,
}


def get_certification_role(slug):
    certification_code = CERTIFIED_CIRCLE_SLUGS.get(slug, None)
    if not certification_code:
        return None
    return CertificationRole.objects.get(code=certification_code)


def adding_certification_required():

    for key, certification_code in CERTIFIED_CIRCLE_SLUGS.items():
        circle = Circle.objects.get(slug=key)
        certification_role = get_certification_role(key)
        circle.certification_required = certification_role
        circle.save()

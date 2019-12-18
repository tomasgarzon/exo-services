from actstream.models import following

from consultant.tasks.hubspot_integrations import HubspotContactConvertToMemberTask
from ..models import Circle
from ..conf import settings


def consultant_to_ecosystem_handler(sender, consultant, *args, **kwargs):
    for circle in Circle.objects.filter(name__in=settings.CIRCLES_FOR_CONSULTANTS):
        circle.add_user(consultant.user)

    # Report to Hubspot
    HubspotContactConvertToMemberTask().s(email=consultant.user.email).apply_async()


def consultant_to_ecosystem_handler_disable(sender, consultant, *args, **kwargs):
    for circle in following(consultant.user, Circle):
        circle.remove_user(consultant.user)

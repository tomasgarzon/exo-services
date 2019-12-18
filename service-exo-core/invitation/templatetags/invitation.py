from django import template

from ..models import Invitation
from ..conf import settings

register = template.Library()


@register.simple_tag
def get_invitation_object(related_object):
    invitation = None
    try:
        invitation = Invitation.objects.filter_by_object(related_object).get()
    except Invitation.MultipleObjectsReturned:
        invitation = Invitation.objects.filter_by_object(related_object).first()
    except Invitation.DoesNotExist:
        pass

    return invitation


@register.simple_tag
def get_email_send(invitation):
    return invitation.logs.filter(
        log_type=settings.INVITATION_CH_TYPE_LOG_SEND,
    ).last()

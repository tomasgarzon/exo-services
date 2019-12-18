# django imports
from django import template

from mailer.models import MessageLog, get_message_id

register = template.Library()


@register.filter
def get_status(message):
    try:
        return MessageLog.objects.filter(message_id=get_message_id(message.email)).last().get_result_display()
    except AttributeError:
        return '-'

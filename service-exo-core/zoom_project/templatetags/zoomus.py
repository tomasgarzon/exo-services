from django import template

from ..models import ZoomMeetingStatus

register = template.Library()


@register.simple_tag(takes_context=True)
def get_last_meeting(context, team):
    try:
        meetings = ZoomMeetingStatus.objects.filter_by_team(team)
        return meetings.actives()[0]
    except IndexError:
        return None

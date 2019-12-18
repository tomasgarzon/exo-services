from django.conf import settings

from circles.helpers import get_announcements_circle, get_question_projects_circle
from .models import Answer, Post


def get_topic_by_object(obj):
    topic = settings.FORUM_TOPIC_DEFAULT

    if isinstance(obj, Answer):
        obj = obj.post

    if isinstance(obj, Post) and obj.qa_session:
        topic = settings.FORUM_TOPIC_SWARM

    return topic


def get_circle_by_object(obj):
    circle = None

    if isinstance(obj, Answer):
        obj = obj.post

    if isinstance(obj, Post):
        if obj.is_circle:
            circle = obj.circle
        elif obj.is_announcement:
            circle = get_announcements_circle()
        elif obj.is_project:
            circle = get_question_projects_circle()

    return circle

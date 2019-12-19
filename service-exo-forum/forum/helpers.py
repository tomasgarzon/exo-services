from django.conf import settings

from .models import Answer, Post


def get_topic_by_object(obj):
    topic = settings.FORUM_TOPIC_DEFAULT

    if isinstance(obj, Answer):
        obj = obj.post

    if isinstance(obj, Post) and obj.qa_session:
        topic = settings.FORUM_TOPIC_SWARM

    return topic

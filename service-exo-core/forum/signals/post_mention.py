from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from actstream import action
from actstream.actions import follow

from exo_mentions.exceptions import MentionedObjectDoesNotExist


def _post_and_answer_mention_detected(user_from, user_to, target):
    action.send(
        user_from,
        action_object=user_to,
        target=target,
        verb=settings.MENTION_VERB)

    follow(user_to, target)


def post_detect_mention_callback(sender, **kwargs):
    object_pk = kwargs.get('object_pk')
    try:
        user_from = kwargs.get('user_from')
        user_to = get_user_model().objects.get(pk=object_pk)
        post = kwargs.get('target')

        if user_from.pk != user_to.pk and not post.qa_session:
            _post_and_answer_mention_detected(
                user_from=user_from,
                user_to=user_to,
                target=post)
            post.send_new_post_mention(user_mentioned=user_to)

    except ObjectDoesNotExist:
        raise MentionedObjectDoesNotExist(
            'Mentioned User with #id {} does not exist'.format(object_pk))


def answer_detect_mention_callback(sender, **kwargs):
    object_pk = kwargs.get('object_pk')
    try:
        user_from = kwargs.get('user_from')
        user_to = get_user_model().objects.get(pk=object_pk)
        answer = kwargs.get('target')

        if user_from.pk != user_to.pk and not answer.post.qa_session:
            _post_and_answer_mention_detected(
                user_from=user_from,
                user_to=user_to,
                target=answer)
            answer.post.send_new_answer_mention(
                answer=answer,
                user_mentioned=user_to)

    except ObjectDoesNotExist:
        raise MentionedObjectDoesNotExist(
            'Mentioned User with #id {} does not exist'.format(object_pk))

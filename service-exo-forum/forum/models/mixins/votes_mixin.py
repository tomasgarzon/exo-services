from django.contrib.contenttypes.models import ContentType

from actstream import action

from ...conf import settings
from ...signals_define import new_action_post, new_action_answer


class VoteMixin:

    @property
    def counter_up_votes(self):
        return self.action_object_actions.filter(
            verb=settings.FORUM_ACTION_UP_VOTE).count()

    @property
    def counter_down_votes(self):
        return self.action_object_actions.filter(
            verb=settings.FORUM_ACTION_DOWN_VOTE).count()

    @property
    def up_votes_user(self):
        return set(self.action_object_actions.filter(
            verb=settings.FORUM_ACTION_UP_VOTE).values_list(
                'actor_object_id', flat=True))

    @property
    def down_votes_user(self):
        return set(self.action_object_actions.filter(
            verb=settings.FORUM_ACTION_DOWN_VOTE).values_list(
                'actor_object_id', flat=True))

    def clear_previous_votes(self, user_from):
        queryset_down_vote = self.action_object_actions.filter(
            actor_content_type=ContentType.objects.get_for_model(user_from),
            actor_object_id=user_from.pk,
            verb=settings.FORUM_ACTION_DOWN_VOTE)
        if queryset_down_vote.exists():
            queryset_down_vote.delete()
        queryset_up_vote = self.action_object_actions.filter(
            actor_content_type=ContentType.objects.get_for_model(user_from),
            actor_object_id=user_from.pk,
            verb=settings.FORUM_ACTION_UP_VOTE)
        if queryset_up_vote.exists():
            queryset_up_vote.delete()

    @property
    def is_post(self):
        ct = ContentType.objects.get_for_model(self)
        return ct.model == 'post'

    def do_like(self, user_from, timestamp=None):
        self.can_vote(user_from)
        self.clear_previous_votes(user_from)
        data = {
            'verb': settings.FORUM_ACTION_UP_VOTE,
            'action_object': self,
        }
        if timestamp:
            data['timestamp'] = timestamp
        action.send(
            user_from,
            **data)

        if self.is_post:
            new_action_post.send(
                sender=self.__class__, instance=self,
                action=settings.FORUM_ACTION_UP_VOTE,
            )
        else:
            new_action_answer.send(
                sender=self.__class__, instance=self,
                action=settings.FORUM_ACTION_UP_VOTE,
            )

    def have_liked(self, user_from):
        return str(user_from.id) in self.up_votes_user

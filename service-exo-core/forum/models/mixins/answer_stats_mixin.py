from actstream import action

from django.contrib.contenttypes.models import ContentType

from ...conf import settings
from .votes_mixin import VoteMixin


class AnswerStatsMixin(VoteMixin):
    def see(self, user_from):
        if not self.has_seen(user_from):
            data = {
                'verb': settings.STATS_ACTION_GENERIC_SEE,
                'action_object': self,
                'target': self.post,
            }
            action.send(user_from, **data)

    def has_seen(self, user):
        user_ct = ContentType.objects.get_for_model(user)
        post_ct = ContentType.objects.get_for_model(self.post)
        return self.action_object_actions.filter(
            actor_content_type=user_ct,
            actor_object_id=user.id,
            target_content_type=post_ct,
            target_object_id=self.post.id,
            verb=settings.STATS_ACTION_GENERIC_SEE).exists()

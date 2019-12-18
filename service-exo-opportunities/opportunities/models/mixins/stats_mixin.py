from actstream import action

from django.contrib.contenttypes.models import ContentType

from ...conf import settings


class ActionStatsMixin():

    def can_see(self, user_from, raise_exceptions=True):
        """
        Default method to validate if user can see the object
        """
        return True

    def see(self, user_from, timestamp=None, notify=True, raise_exceptions=False):
        self.can_see(user_from=user_from, raise_exceptions=raise_exceptions)
        action_verb = settings.OPPORTUNITIES_ACT_ACTION_SEE
        data = {
            'verb': action_verb,
            'action_object': self,
        }
        if timestamp:
            data['timestamp'] = timestamp

        action.send(user_from, **data)

    def has_seen(self, user):
        ct = ContentType.objects.get_for_model(user)
        return self.action_object_actions.filter(
            actor_content_type=ct,
            actor_object_id=str(user.id),
            verb=settings.OPPORTUNITIES_ACT_ACTION_SEE).exists()

    def last_see_timestamp(self, user):
        ct = ContentType.objects.get_for_model(user)
        last_see_action = self.action_object_actions.filter(
            actor_content_type=ct,
            actor_object_id=str(user.id),
            verb=settings.OPPORTUNITIES_ACT_ACTION_SEE).first()
        timestamp = None
        if last_see_action:
            timestamp = last_see_action.timestamp
        return timestamp

    def total_unread(self, user, conversations):
        timestamp = self.last_see_timestamp(user)
        return sum([conversation.total_unread(user, timestamp) for conversation in conversations])

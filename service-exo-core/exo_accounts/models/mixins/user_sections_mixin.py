from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from actstream import action


class UserSectionsMixin:

    def get_sections_visited(self):
        sections = []

        for section in settings.EXO_ACCOUNTS_SECTIONS_VISITED_AVAILABLE:
            if self.has_seen_section(section):
                sections.append(section)
        return sections

    @property
    def sections_visited(self):
        return self.get_sections_visited()

    def see_section(self, section):
        action_verb = settings.STATS_ACTION_GENERIC_SEE
        data = {
            'verb': action_verb,
            'action_object': self,
            'description': section,
        }

        action.send(self, **data)

    def has_seen_section(self, section):
        ct = ContentType.objects.get_for_model(self)
        return self.action_object_actions.filter(
            actor_content_type=ct,
            actor_object_id=self.id,
            verb=settings.STATS_ACTION_GENERIC_SEE,
            description=section).exists()

from ...models import Keyword
from .keyword import KeywordSerializer


class KeywordSerializerMixin:

    keywords = KeywordSerializer(many=True, required=False)

    def sync_tags(self, tags, user):
        return Keyword.objects.update_keywords(
            user_from=user,
            keywords_name=[k['name'] for k in tags],
        )

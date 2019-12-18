from utils.drf import DALAutocomplete

from ...models import Tag


class TagAutocomplete(DALAutocomplete):
    model = Tag

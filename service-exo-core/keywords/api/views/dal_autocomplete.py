from django.db.models import Q

from utils.drf import DALAutocomplete

from ...models import Keyword


class KeywordAutocomplete(DALAutocomplete):
    model = Keyword
    paginate_by = 1000

    def get_queryset(self):
        q2 = Q(public=True)
        if self.request.GET.get('tags'):
            q1 = Q(tags__name=self.request.GET.get('tags'))
            return super().get_queryset().filter(q1 & q2)
        return super().get_queryset().filter(q2)

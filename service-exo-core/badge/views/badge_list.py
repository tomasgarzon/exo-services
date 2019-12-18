from django.db.models import Q
from utils.generic.list import ListFilterView

from ..models import UserBadge
from ..forms import BadgeSearchListForm
from .mixins import UserBadgeSectionViewMixin


class UserBadgeListView(UserBadgeSectionViewMixin, ListFilterView):
    model = UserBadge
    paginate_by = 10
    template_name = 'badge/list.html'
    filter_form_class = BadgeSearchListForm
    raise_exception = True

    def get_queryset(self):
        queryset = self.model.objects.all()
        search = self.form_filter.data.get('search', None)

        if search:
            query = Q(user__full_name__icontains=search) \
                | Q(user__email__icontains=search) \

            queryset = queryset.filter(query)

        return queryset.order_by('user__full_name', 'badge__category')

from django.contrib.auth.mixins import PermissionRequiredMixin

from ..models import UserBadge
from ..conf import settings


class UserBadgeSectionViewMixin(PermissionRequiredMixin):
    model = UserBadge
    permission_required = settings.BADGE_FULL_PERMISSION_ADD_BADGE

    def get_queryset(self):
        return self.model.objects.all()

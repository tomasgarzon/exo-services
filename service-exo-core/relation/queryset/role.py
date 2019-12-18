from django.db.models import QuerySet
from django.contrib.auth import get_user_model

from ..conf import settings


class RoleQuerySet(QuerySet):

    def actives_only(self):
        return self.filter(status=settings.RELATION_ROLE_CH_ACTIVE)

    def roles(self):
        return self.values_list('exo_role', flat=True)

    def only_visible(self):
        return self.filter(visible=True)

    def users(self):
        user_ids = self.values_list('user_id', flat=True)
        return get_user_model().objects.filter(id__in=user_ids)


class ExORoleQuerySet(RoleQuerySet):

    def filter_by_exo_role(self, exo_role):
        return self.filter(exo_role=exo_role)

    def filter_by_exo_role_code(self, code):
        return self.filter(exo_role__code=code)

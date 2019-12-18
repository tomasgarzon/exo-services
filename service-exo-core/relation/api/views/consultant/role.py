from rest_framework import viewsets

from ...serializers.consultant.role import ConsultantRoleSerializer
from .mixin import ConsultantViewSetMixin


class ConsultantRoleViewSet(
        ConsultantViewSetMixin,
        viewsets.ModelViewSet
):

    serializer_class = ConsultantRoleSerializer
    swagger_schema = None

    def get_queryset(self):
        consultant = self.get_consultant()
        return consultant.consultant_roles.all()

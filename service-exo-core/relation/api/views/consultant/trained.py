from rest_framework import viewsets

from ...serializers.consultant.trained import ConsultantTrainedSerializer
from .mixin import ConsultantViewSetMixin


class ConsultantTrainedViewSet(
        ConsultantViewSetMixin,
        viewsets.ModelViewSet
):
    serializer_class = ConsultantTrainedSerializer
    swagger_schema = None

    def get_queryset(self):
        consultant = self.get_consultant()
        return consultant.trained_sessions.all()

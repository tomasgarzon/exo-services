from djangorestframework_camel_case.render import CamelCaseJSONRenderer

from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated

from .mixins import QASessionGenericViewMixin
from ..serializers.qa_session_rest import QASessionEcosystemSerializer
from ...models import QASession


class QASessionEcosystemViewSet(
        mixins.RetrieveModelMixin,
        QASessionGenericViewMixin):
    permission_classes = (IsAuthenticated, )
    renderer_classes = (CamelCaseJSONRenderer,)
    queryset = QASession.objects.all()
    serializers = {
        'default': QASessionEcosystemSerializer,
    }

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return self.queryset

        return self.queryset.filter(members__consultant__user=user)

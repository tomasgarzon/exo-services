from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from djangorestframework_camel_case.render import CamelCaseJSONRenderer

from ..serializers.exo_activity import ExOActivitySerializer
from ...models import ExOActivity


class ExOActivityViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    model = ExOActivity
    renderer_classes = (CamelCaseJSONRenderer, )
    serializer_class = ExOActivitySerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.model.objects.all()

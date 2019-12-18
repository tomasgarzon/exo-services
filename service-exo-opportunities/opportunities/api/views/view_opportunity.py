from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from ...models import Opportunity
from ..serializers import opportunity_view


class OpportunityRetrieveViewSet(
        mixins.RetrieveModelMixin,
        viewsets.GenericViewSet):

    model = Opportunity
    permission_classes = (IsAuthenticated,)
    serializer_class = opportunity_view.OpportunitySerializer
    lookup_field = 'uuid'

    def get_queryset(self):
        return self.model.objects.all()

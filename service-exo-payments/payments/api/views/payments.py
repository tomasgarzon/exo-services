from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated

from ...models import Payment
from ..serializers import DoRequestSerializer


class DoRequestPaymentView(CreateAPIView):
    model = Payment
    serializer_class = DoRequestSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user)

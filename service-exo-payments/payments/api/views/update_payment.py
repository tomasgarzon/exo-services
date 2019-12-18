from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import IsAuthenticated

from utils.username_authentication import UsernameAuthentication

from ...models import Payment
from ..serializers import UpdatePaymentSerializer


class UpdatePaymentView(UpdateAPIView):
    serializer_class = UpdatePaymentSerializer
    permission_classes = (IsAuthenticated, )
    authentication_classes = (UsernameAuthentication, )
    queryset = Payment.objects.all()
    lookup_field = 'uuid'

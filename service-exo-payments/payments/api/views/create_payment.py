from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated

from utils.username_authentication import UsernameAuthentication

from ...models import Payment
from ..serializers import CreatePaymentSerializer


class CreatePaymentView(CreateAPIView):
    model = Payment
    serializer_class = CreatePaymentSerializer
    permission_classes = (IsAuthenticated, )
    authentication_classes = (UsernameAuthentication, )

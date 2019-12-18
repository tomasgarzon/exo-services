from rest_framework.generics import UpdateAPIView

from ...models import Payment
from ..serializers import EmailNotifySerializer


class EmailNotifyView(UpdateAPIView):

    model = Payment
    serializer_class = EmailNotifySerializer
    lookup_field = '_hash_code'
    lookup_url_kwarg = 'hash'

    def get_queryset(self):
        return Payment.objects.all()

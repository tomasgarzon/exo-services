from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from utils.drf.authentication import UsernameAuthentication

from ...models import Opportunity
from ..serializers.migrate_ticket import MigrateTicketSerializer


class MigrateTicketViiew(generics.CreateAPIView):
    model = Opportunity
    serializer_class = MigrateTicketSerializer
    authentication_classes = (UsernameAuthentication, )
    permission_classes = (IsAuthenticated,)

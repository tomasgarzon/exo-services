from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from ...models import Message
from ..serializers.message import MessageSerializer


class MessageViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):

    model = Message
    serializer_class = MessageSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.model.objects.filter(
            created_by=self.request.user,
        )

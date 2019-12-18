from django.contrib.auth import get_user_model
from django.views.generic.detail import SingleObjectMixin

from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response

from ..serializers.conversation import StartConversationSerializer


class StartConversationView(
        SingleObjectMixin,
        CreateAPIView):

    model = get_user_model()
    permission_classes = [IsAuthenticated]
    return_404 = True
    serializer_class = StartConversationSerializer

    def get_queryset(self):
        return get_user_model().objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            user_from=request.user,
            user_to=self.get_object()
        )
        return Response({}, status=status.HTTP_201_CREATED)

from django.contrib.auth import get_user_model

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from ..serializers.user_signup import UserSignupSerializer


class UserSignupView(generics.CreateAPIView):
    model = get_user_model()
    serializer_class = UserSignupSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.model.objects.all()

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth import get_user_model

from consultant.api.serializers.requirement import RequirementSerializer


class UserRequirementView(generics.ListAPIView):
    serializer_class = RequirementSerializer
    model = get_user_model()
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.model.objects.filter(id=self.request.user.id)

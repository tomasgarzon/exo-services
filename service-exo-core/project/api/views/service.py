from rest_framework import generics

from utils.drf import SuccessMessageMixin

from ..serializers.service import ServiceCreateSerializer


class ServiceCreateView(SuccessMessageMixin, generics.CreateAPIView):

    serializer_class = ServiceCreateSerializer
    model = serializer_class.Meta.model
    success_message = '%(name)s was created successfully'

    def perform_create(self, serializer):
        serializer.save(user_from=self.request.user)
        self.set_success_message(serializer.data)

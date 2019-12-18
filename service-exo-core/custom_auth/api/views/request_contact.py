from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ..serializers.request_contact import RequestContactSerializer


class UserRequestContactView(APIView):
    serializer_class = RequestContactSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        serializer = self.serializer_class(
            data=request.data,
            context={'user_from': request.user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

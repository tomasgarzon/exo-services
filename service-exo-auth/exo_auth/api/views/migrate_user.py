from rest_framework import views, response
from rest_framework.permissions import IsAuthenticated

from utils.authentication import UsernameAuthentication

from ..serializers.migrate_user import MigrateUserSeriailzer


class MigrateUserView(views.APIView):
    serializer_class = MigrateUserSeriailzer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (UsernameAuthentication,)

    def post(self, request, format='json'):
        serializer = self.serializer_class(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response()

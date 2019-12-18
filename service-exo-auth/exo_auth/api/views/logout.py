from django.contrib.auth import (
    logout as django_logout
)

from django.utils.translation import ugettext_lazy as _

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny


class LogoutView(APIView):
    """
    Calls Django logout method and delete the Token object
    assigned to the current User object.

    Accepts/Returns nothing.
    """
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        response = self.logout(request)

        return self.finalize_response(request, response, *args, **kwargs)

    def post(self, request):
        return self.logout(request)

    def logout(self, request):
        django_logout(request)

        return Response(
            {'detail': _('Successfully logged out.')},
            status=status.HTTP_200_OK,
        )

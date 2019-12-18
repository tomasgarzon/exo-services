from django.http import JsonResponse

from rest_framework import status


class ApiNoPermissionsResponseMixin:

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except PermissionError:  # noqa
            return JsonResponse(
                {'error': 'Operation not permitted'},
                status=status.HTTP_403_FORBIDDEN
            )

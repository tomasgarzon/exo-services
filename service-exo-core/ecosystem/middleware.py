from django.contrib import auth
from django.core.exceptions import ObjectDoesNotExist

from .models import Member


class EcosystemActivityMiddleware:
    EXTENSIONS_EXCLUDED = ['js', 'map', 'css']
    PATHS_EXCLUDED = ['/api/graphql-jwt']

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = self._get_user(request)
        if user.is_authenticated and \
                request.method in ['POST', 'PUT', 'DELETE']:

            try:
                member = Member.objects.get(user=user)
                member.update_activity()
            except ObjectDoesNotExist:
                pass

        return self.get_response(request)

    def _get_user(self, request):
        if not hasattr(request, '_cached_user'):
            request._cached_user = auth.get_user(request)
        return request._cached_user

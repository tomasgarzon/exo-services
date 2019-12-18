from django.utils.functional import SimpleLazyObject
from django.contrib.auth.middleware import get_user
from django.utils.deprecation import MiddlewareMixin
from rest_framework.request import Request
from rest_framework_jwt.authentication import JSONWebTokenAuthentication


def get_user_jwt(request):
    user = get_user(request)
    if user.is_authenticated:
        return user
    try:
        user_jwt = JSONWebTokenAuthentication().authenticate(Request(request))
        if user_jwt is not None:
            return user_jwt[0]
    except Exception:
        pass
    return user


class JWTAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        assert hasattr(request, 'session'), (
            'The Django authentication middleware requires session middleware '
            'to be installed. Edit your MIDDLEWARE_CLASSES setting to insert '
            "'django.contrib.sessions.middleware.SessionMiddleware'."
        )
        if request.user.is_anonymous:
            request.user = SimpleLazyObject(lambda: get_user_jwt(request))

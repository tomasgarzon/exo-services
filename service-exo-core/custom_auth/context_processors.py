from .jwt_helpers import _build_jwt


def jwt(request):
    user = request.user
    if user.is_authenticated:
        token = _build_jwt(user)
        return {
            'jwt': token,
        }
    return {}

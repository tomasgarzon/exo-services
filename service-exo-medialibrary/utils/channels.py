from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

from channels.sessions import CookieMiddleware, SessionMiddleware
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from channels.auth import UserLazyObject


@database_sync_to_async
def get_user(scope):
    """
    Return the user model instance associated with the given scope.
    If no user is retrieved, return an instance of `AnonymousUser`.
    """
    if "cookies" not in scope:
        raise ValueError(
            "Cannot find cookies in scope. You should wrap your consumer in CookiesMiddleware."
        )
    cookies = scope["cookies"]
    user = None
    try:
        user = _get_user_session_key(cookies)
    except Exception:
        pass

    return user or AnonymousUser()


def _get_user_session_key(cookies):
    # This value in the session is always serialized to a string, so we need
    # to convert it back to Python whenever we access it.
    return get_user_model().objects.retrieve_remote_user_by_cookie(cookies)


class AuthMiddleware(BaseMiddleware):
    """
    Middleware which populates scope["user"] from a Django session.
    Requires SessionMiddleware to function.
    """

    def populate_scope(self, scope):
        # Make sure we have a session
        if "session" not in scope:
            raise ValueError(
                "AuthMiddleware cannot find session in scope. SessionMiddleware must be above it."
            )
        # Add it to the scope if it's not there already
        if "user" not in scope:
            scope["user"] = UserLazyObject()

    async def resolve_scope(self, scope):
        scope["user"]._wrapped = await get_user(scope)


# Handy shortcut for applying all three layers at once
AuthMiddlewareStack = lambda inner: CookieMiddleware(
    SessionMiddleware(AuthMiddleware(inner))
)

from django.conf import settings
import jwt
from datetime import datetime


def jwt_get_username_from_payload_handler(payload):
    return payload.get('uuid')


def jwt_decode_handler(token):
    options = {
        'verify_exp': settings.JWT_VERIFY_EXPIRATION,
    }

    return jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        settings.JWT_VERIFY,
        options=options,
        leeway=settings.JWT_LEEWAY,
        audience=settings.JWT_AUDIENCE,
        issuer=settings.JWT_ISSUER,
        algorithms=[settings.JWT_ALGORITHM]
    )


def jwt_payload_handler(user):
    return {
        'user_id': str(user.id),
        'uuid': str(user.id),
        'exp': datetime(2100, 1, 1),
    }

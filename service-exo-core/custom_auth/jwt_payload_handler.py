from datetime import datetime


def jwt_payload_handler(user):
    return {
        'user_id': user.id,
        'uuid': str(user.uuid),
        'email': user.email,
        'username': user.username,
        'exp': datetime(2100, 1, 1),
    }

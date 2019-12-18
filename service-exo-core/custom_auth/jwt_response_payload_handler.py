from .api.serializers.user import UserSerializer


def jwt_response_payload_handler(token, user=None, request=None):
    """
    Returns the response data for both the login and refresh views.
    Override to return a custom response such as including the
    serialized representation of the User.
    """
    return {
        'token': token,
        'user': UserSerializer(user).data,
    }


def jwt_get_username_from_payload_handler(payload):
    return payload.get('uuid')

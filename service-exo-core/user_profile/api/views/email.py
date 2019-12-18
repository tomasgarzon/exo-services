from ..serializers.email import ChangeEmailSerializer
from .profile_mixin import UpdateProfileMixin


class UpdateEmailView(UpdateProfileMixin):
    """
    Use this endpoint to change user email.
    """
    serializer_class = ChangeEmailSerializer

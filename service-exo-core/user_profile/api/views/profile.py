from ..serializers.profile_summary import ProfileSummarySerializer
from ..serializers.version2 import SummarySerializer, AboutYouSerializer
from .profile_mixin import UpdateProfileMixin


class UpdateProfileSummaryView(UpdateProfileMixin):
    """
    Use this endpoint to change user profile summary.
    """
    serializer_class = ProfileSummarySerializer


class ProfileSummaryView(UpdateProfileMixin):
    serializer_class = SummarySerializer


class ProfileAboutYouView(UpdateProfileMixin):
    serializer_class = AboutYouSerializer
    swagger_schema = None

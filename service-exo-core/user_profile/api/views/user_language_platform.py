from django.conf import settings

from ..serializers.language import LanguagePlattformSerializer
from .profile_mixin import UpdateProfileMixin


class UserLanguagePlattformView(UpdateProfileMixin):
    serializer_class = LanguagePlattformSerializer

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)

        self.request.user.refresh_from_db()
        response.set_cookie(
            settings.LANGUAGE_COOKIE_NAME,
            self.request.user.platform_language,
        )
        return response

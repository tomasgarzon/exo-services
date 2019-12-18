from django.db.models import QuerySet

from django.conf import settings


class RegistrationProcessQuerySet(QuerySet):

    def filter_by_content_object_pending(self, object_id, content_type_id):
        return self.filter(
            steps__status=settings.REGISTRATION_CH_CURRENT,
            steps__object_id=object_id,
            steps__content_type_id=content_type_id,
        )

    def filter_by_content_object(self, object_id, content_type_id):
        return self.filter(
            steps__object_id=object_id,
            steps__content_type_id=content_type_id,
        )

    def filter_by_current_status(self, value):
        return self.filter(
            steps__status=settings.REGISTRATION_CH_CURRENT,
            steps__code=value)

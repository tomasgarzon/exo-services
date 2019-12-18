from ..conf import settings
from .base import BaseValidator


class TeamZoomValidator(BaseValidator):

    def validate(self):
        validation_status = None
        zoom_rooms = None
        try:
            zoom_settings = self.project.zoom_settings
            zoom_rooms = zoom_settings.teams_zoom_rooms
        except Exception:
            pass

        if self.project.teams.count() and zoom_rooms:
            validation, _ = self.project.validations.get_or_create(
                validation_detail=settings.VALIDATION_CH_NO_ZOOM,
                defaults={
                    'validation_type': settings.VALIDATION_CH_WARNING,
                    'content_object': self.project.zoom_settings,
                    'subject': settings.VALIDATION_LABEL_VALIDATION[
                        settings.VALIDATION_CH_NO_ZOOM
                    ],
                },
            )

            all_zoom_rooms_created = zoom_rooms.count() == self.project.teams.count()
            all_zoom_host_meeting_id_ok = zoom_rooms.filter(
                host_meeting_id__isnull=False,
            ).count() == self.project.teams.count()

            if all_zoom_rooms_created and all_zoom_host_meeting_id_ok:
                validation.fixed()
            else:
                validation.pending()

            validation_status = validation.is_pending

        return validation_status

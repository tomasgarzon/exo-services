from django.conf import settings


class ZoomifyMixin:
    """
     How to use:
        - Add this mixin to Model
        - Create a property using the ZOOM_SETTINGS_FIELD or re-define on the model
        - Create a new field and use DEFAULT_ROOM_FIELD to reference
            define in that way (Team example):
                _room = GenericRelation(
                    'zoom_project.ZoomRoom',
                    related_query_name='teams')
    """

    ZOOM_SETTINGS_FIELD = '_zoom_settings'
    DEFAULT_ROOM_FIELD = '_room'

    @property
    def settings(self):
        return getattr(self, self.ZOOM_SETTINGS_FIELD)

    @property
    def room(self):
        return self._room.first()

    @property
    def zoom_id(self):
        meeting_id = None
        if self.room:
            meeting_id = self.room.meeting_id

        return meeting_id

    @zoom_id.setter
    def zoom_id(self, meeting_id):
        if not self.room and meeting_id and self.id and self.settings:
            getattr(
                self,
                self.DEFAULT_ROOM_FIELD,
            ).create(
                content_object=self,
                _zoom_settings=self.settings,
            )

        if self.room:
            room = self.room
            room.meeting_id = meeting_id
            room.save(update_fields=['meeting_id'])

    @property
    def join_url(self):
        """
        URL for clients
        """
        url = None
        if self.room and self.room.meeting_id:
            url = '{}/{}'.format(
                settings.ZOOM_PROJECT_JOIN_URL,
                self.room.meeting_id.replace('-', ''),
            )

        return url

    @property
    def start_url(self):
        """
        URL for the host
        """
        url = None
        if self.room and self.room.meeting_id and self.room.host_meeting_id:
            url = '{}/{}?{}={}'.format(
                settings.ZOOM_PROJECT_START_URL,
                self.room.meeting_id.replace('-', ''),
                settings.ZOOM_PROJECT_TOKEN_NAME,
                self.room.host_meeting_id.replace('-', ''),
            )

        return url

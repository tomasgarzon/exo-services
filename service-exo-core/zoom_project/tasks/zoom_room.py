from celery import Task

from ..models import ZoomRoom


class UpdateZoomRoomTask(Task):
    name = 'UpdateZoomRoomTask'

    def run(self, zoom_room_id):
        """
            Update Join url Zoom Token param for this room
        """
        zoom_room = ZoomRoom.objects.get(pk=zoom_room_id)
        zoom_room.update_host_meeting_id()


class ScheduleMeetingTask(Task):
    name = 'ScheduleMeetingTask'

    def run(self, zoom_room_id, title, start, timezone):
        """
            Schedule a meeting for this zoom_id
        """
        zoom_room = ZoomRoom.objects.get(pk=zoom_room_id)
        zoom_room.schedule_meeting(title, start, timezone, 60)

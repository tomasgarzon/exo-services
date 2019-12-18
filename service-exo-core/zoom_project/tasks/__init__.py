from celery import current_app as app

from .zoom_room import UpdateZoomRoomTask, ScheduleMeetingTask


app.tasks.register(UpdateZoomRoomTask())
app.tasks.register(ScheduleMeetingTask())

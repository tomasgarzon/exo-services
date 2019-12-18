from ..tasks import UpdateZoomRoomTask


def post_save_room(sender, instance, created, *args, **kwargs):
    update_fields = kwargs.get('update_fields') or []
    if (created and instance.meeting_id) or 'meeting_id' in update_fields:
        if instance.meeting_id:
            if instance.teams.exists():
                task = UpdateZoomRoomTask()
                task.apply_async(
                    kwargs={'zoom_room_id': instance.id})

from django.conf import settings
from django.contrib.auth import get_user_model

from utils.dates import find_place_id, find_address

from celery import Task


User = get_user_model()


class UserLocationTask(Task):
    name = 'UserLocationTask'
    ignore_result = True

    def run(self, *args, **kwargs):
        user = User.objects.get(pk=kwargs.get('user_id'))
        if settings.POPULATOR_MODE:
            return
        if user.location is None:
            return
        if user.place_id is None:
            place_id = find_place_id(user.location)
            if not place_id:
                return
            user.place_id = place_id
        location = find_address(user.place_id)
        if location is None:
            return
        user.location = location
        user.save()

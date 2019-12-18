from django.conf import settings
from django.contrib.auth.models import Group


def group_waiting_list():
    group, _ = Group.objects.get_or_create(
        name=settings.CONSULTANT_WAITING_LIST_GROUP_NAME)
    return group

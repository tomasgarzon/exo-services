from django.contrib.auth import get_user_model
from django.contrib.admin.utils import NestedObjects


def merge_users(user, user_uuid):
    existing_user, created = get_user_model().objects.get_or_create(
        uuid=user_uuid,
        defaults={'is_active': True})

    collector = NestedObjects(using='default')
    collector.collect([user])
    to_change_user = collector.nested()
    try:
        related_objects = to_change_user[1]
    except IndexError:
        related_objects = []
    for related_object in related_objects:
        if getattr(related_object, 'user', None) == user:
            related_object.user = existing_user
            related_object.save()
        if getattr(related_object, 'created_by', None) == user:
            related_object.created_by = existing_user
            related_object.save()

    for group in user.communication_groups.all():
        group.users.add(existing_user)
    if hasattr(existing_user, 'participant'):
        participant = existing_user.participant
        participant.delete()
    user.delete()

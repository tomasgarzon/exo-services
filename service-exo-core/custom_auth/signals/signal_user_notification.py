from django.conf import settings

from utils import notifications

from ..api.serializers.user import UserSerializer


def send_user(instance):
    serializer = UserSerializer(instance)
    notifications.send_notifications(
        settings.CUSTOM_AUTH_USER_TOPIC,
        'update',
        instance.__class__.__name__.lower(),
        instance.uuid,
        serializer.data)


def signal_user_post_save_handler(sender, instance, created, *args, **kwargs):
    if not created:
        send_user(instance)


def signal_user_permissions_handler(sender, instance, action, *args, **kwargs):
    if action in['post_add', 'post_remove']:
        send_user(instance)

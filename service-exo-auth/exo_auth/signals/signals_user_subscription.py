from ..models import UserSubscription
from ..tasks import new_user_connected, user_disconnected


def create_user_subscription_handler(sender, instance, *args, **kwargs):
    created = kwargs.get('created')
    if created:
        uuids_in_topic = UserSubscription.objects.filter(
            subscription=instance.subscription
        ).values_list('user_uuid', flat=True)
        new_user_connected.delay(list(uuids_in_topic), instance.user_uuid.__str__())


def delete_user_subscription_handler(sender, instance, *args, **kwargs):
    uuids_in_topic = UserSubscription.objects.filter(
        subscription=instance.subscription
    ).values_list('user_uuid', flat=True)
    user_disconnected.delay(list(uuids_in_topic), instance.user_uuid.__str__())

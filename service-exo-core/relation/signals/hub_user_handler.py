def hub_user_post_save_handler(sender, instance, created, *args, **kwargs):
    if created:
        hub = instance.hub
        if hasattr(hub, 'circle'):
            circle = hub.circle
            circle.add_user(instance.user)


def hub_user_post_delete_handler(sender, instance, *args, **kwargs):
    hub = instance.hub
    if hasattr(hub, 'circle'):
        circle = hub.circle
        circle.remove_user(instance.user)

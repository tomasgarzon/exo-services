
def metrics_handler(sender, instance, *args, **kwargs):
    action_object = None

    if 'following' in instance.verb:
        action_object = instance.target

    else:
        try:
            assert instance.action_object
            action_object = instance.action_object
        except AssertionError:
            has_action_object = instance.action_object_object_id is not None and \
                instance.action_object_content_type is not None
            action_object_class = instance.action_object_content_type.model_class()

            if has_action_object and hasattr(action_object_class, 'all_objects'):
                action_object = action_object_class.all_objects.filter(
                    pk=instance.action_object_object_id).get()

    try:
        action_object.create_new_metric(action=instance)
    except AttributeError:
        pass

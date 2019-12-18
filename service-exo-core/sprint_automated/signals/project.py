
def post_save_project(sender, instance, created, *args, **kwargs):
    update_fields = kwargs.get('update_fields') or []

    if instance.is_sprintautomated and 'start' in update_fields:
        instance.real_type.update_first_step_dates()

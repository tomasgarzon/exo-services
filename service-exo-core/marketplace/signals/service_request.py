def post_save_service_request(sender, instance, created, *args, **kwargs):
    if created:
        instance.notify_managers_email()

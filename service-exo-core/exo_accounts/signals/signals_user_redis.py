
def check_new_active_email_address(sender, instance, *args, **kwargs):
    update_fields = kwargs.get('update_fields', []) or []

    if 'is_primary' in update_fields and not instance.is_primary:
        instance.user.delete_platform_language_from_redis()


def check_redis_user_cache(sender, instance, *args, **kwargs):
    update_fields = kwargs.get('update_fields', []) or []

    if '_platform_language' in update_fields:
        instance.delete_platform_language_from_redis()

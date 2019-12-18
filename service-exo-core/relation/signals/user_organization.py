from exo_accounts.signals_define import signal_exo_user_title


def user_organization_role_post_save(sender, instance, created, *args, **kwargs):
    update_fields = kwargs.get('update_fields') or []
    if (created or 'status' in update_fields) and (instance.is_active):
        signal_exo_user_title.send(sender=sender, instance=instance.user)


def user_organization_role_post_delete(sender, instance, *args, **kwargs):
    signal_exo_user_title.send(sender=sender, instance=instance.user)

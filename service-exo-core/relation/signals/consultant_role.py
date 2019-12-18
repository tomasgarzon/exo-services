from exo_accounts.signals_define import signal_exo_user_title


def consultant_role_post_save(sender, instance, created, *args, **kwargs):
    signal_exo_user_title.send(sender=sender, instance=instance.user)


def consultant_role_post_delete(sender, instance, *args, **kwargs):
    signal_exo_user_title.send(sender=sender, instance=instance.user)

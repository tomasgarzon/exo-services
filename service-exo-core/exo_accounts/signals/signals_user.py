from ..conf import settings
from ..helpers import calculate_user_title
from ..signals_define import signal_username_created, signal_username_updated


def clear_unverified_email_addresses(sender, **kwargs):
    created = kwargs['created']
    user = kwargs['instance']
    if not created and not user.is_active:
        for email in user.emailaddress_set.all():
            if not email.is_verified:
                email.delete()


def post_save_user_perms(sender, instance, created, *args, **kwargs):
    if created:
        instance.add_permission(settings.EXO_ACCOUNTS_PERMS_USER_EDIT, instance)


def post_save_user_username(sender, instance, created, *args, **kwargs):
    if created and not instance.is_consultant:
        instance.generate_public_username()
        signal_username_created.send(
            sender=sender,
            user=instance)
    update_fields = kwargs.get('update_fields', [])
    if not created and update_fields and '_username' in update_fields:
        signal_username_updated.send(
            sender=sender,
            user=instance)


def update_user_title_handler(sender, instance, *args, **kwargs):
    instance.user_title = calculate_user_title(instance)
    instance.save(update_fields=['user_title'])

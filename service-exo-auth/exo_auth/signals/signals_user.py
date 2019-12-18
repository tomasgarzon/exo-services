from guardian.shortcuts import assign_perm

from ..conf import settings


def clear_unverified_email_addresses(sender, **kwargs):
    created = kwargs['created']
    user = kwargs['instance']
    if not created and not user.is_active:
        for email in user.emailaddress_set.all():
            if not email.is_verified:
                email.delete()


def post_save_user_perms(sender, instance, created, *args, **kwargs):
    if created:
        assign_perm(settings.EXO_AUTH_PERMS_USER_EDIT, instance, instance)

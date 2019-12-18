from django.conf import settings

from marketplace.tasks import (
    AddMarketplaceUserPermsTask,
    RemoveMarketplaceUserPermsTask)


def post_save_agreement(sender, instance, created, *args, **kwargs):
    if instance.is_inactive:
        instance.user_agreements.all().update(
            status=settings.AGREEMENT_USER_STATUS_REVOKED)


def post_save_user_agreement(sender, instance, created, *args, **kwargs):
    agreement = instance.agreement

    if agreement.is_marketplace:
        if instance.is_accepted:
            instance.user.add_django_permission(
                settings.EXO_ACCOUNTS_PERMS_MARKETPLACE_FULL)

            AddMarketplaceUserPermsTask().s(
                uuid=instance.user.uuid).apply()

        elif instance.is_revoked:
            instance.user.remove_django_permission(
                settings.EXO_ACCOUNTS_PERMS_MARKETPLACE_FULL)

            RemoveMarketplaceUserPermsTask().s(
                uuid=instance.user.uuid).apply()

    elif agreement.is_exq:
        if instance.is_accepted:
            instance.user.add_django_permission(
                settings.EXO_ACCOUNTS_PERMS_EXQ_FULL)
        elif instance.is_revoked:
            instance.user.remove_django_permission(
                settings.EXO_ACCOUNTS_PERMS_EXQ_FULL)


def post_delete_user_agreement(sender, instance, *args, **kwargs):
    agreement = instance.agreement

    if agreement.is_marketplace:
        instance.user.remove_django_permission(
            settings.EXO_ACCOUNTS_PERMS_MARKETPLACE_FULL)

        RemoveMarketplaceUserPermsTask().s(
            uuid=instance.user.uuid).apply()

    elif agreement.is_exq:
        instance.user.remove_django_permission(
            settings.EXO_ACCOUNTS_PERMS_EXQ_FULL)

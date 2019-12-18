from ecosystem.signals_define import post_save_consultant_signal
from exo_attributes.models import ExOAttribute

from ..conf import settings
from ..models import ConsultantExOProfile


def consultant_post_save_perms(sender, instance, created, *args, **kwargs):
    if created:
        instance.add_permission(
            settings.CONSULTANT_PERMS_CONSULTANT_VIEW_FULL_PROFILE,
            instance.user,
        )
        instance.add_permission(
            settings.CONSULTANT_PERMS_CONSULTANT_EDIT_PROFILE,
            instance.user,
        )

        # Create default ExO Profile
        ConsultantExOProfile.objects.create(consultant=instance)

        # Create default ExO Attributes
        for attr in ExOAttribute.objects.all():
            instance.exo_attributes.create(exo_attribute=attr)

        post_save_consultant_signal.send(
            sender=instance.__class__,
            consultant=instance)

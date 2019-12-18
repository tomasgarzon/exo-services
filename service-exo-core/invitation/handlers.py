from django.db.models.signals import pre_delete
from django.apps import apps

from utils.signal_receivers import receiver_subclasses

from .models.mixins import DeleteInvitationMixin


@receiver_subclasses(pre_delete, DeleteInvitationMixin, 'invitation_object_delete')
def remove_invitation_object(sender, instance, **kwargs):
    Invitation = apps.get_model('invitation', 'Invitation')
    invitations = Invitation.objects.filter_by_object(instance)
    invitations.delete()

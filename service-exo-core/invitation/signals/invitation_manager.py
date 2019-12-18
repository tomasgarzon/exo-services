from django.apps import apps


def send_invitation_signal_manager(sender, method_name,
                                   from_user, user, send_notification,
                                   *args, **kwargs):
    """
    Manage all signals received, from external apps, related to any kind of object present at Tool,
    and take decissions related to Invitations to send it or whatever.
    """
    if send_notification:
        Invitation = apps.get_model(app_label='invitation', model_name='Invitation')
        invitation_method = getattr(Invitation.objects, method_name)
        invitation_method(from_user=from_user, user=user, *args, **kwargs)

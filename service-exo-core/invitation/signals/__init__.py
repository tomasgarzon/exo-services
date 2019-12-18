from django.apps import apps
from django.db.models.signals import post_save

from exo_accounts.signals_define import signal_exo_accounts_user_created

from .invitation import when_invitation_post_save
from .invitation_manager import send_invitation_signal_manager
from .invitation_object import when_invitation_object_post_save


def parse_external_signal(method_name, *args, **kwargs):
    def inner1(f, *args, **kwargs):
        def inner2(sender, **kwargs):
            f(sender, method_name=method_name, **kwargs)
        return inner2
    return inner1


def setup_signals():
    from ..handlers import receiver_subclasses  # noqa

    Invitation = apps.get_model(
        app_label='invitation',
        model_name='Invitation')
    InvitationObject = apps.get_model(
        app_label='invitation',
        model_name='InvitationObject')
    ExOAccountUser = apps.get_model(
        app_label='exo_accounts',
        model_name='User')

    post_save.connect(
        when_invitation_post_save,
        sender=Invitation)
    post_save.connect(
        when_invitation_object_post_save,
        sender=InvitationObject)

    # ExOAccounts signals
    signal_exo_accounts_user_created.connect(
        parse_external_signal(
            method_name='create_simple_signup_invitation'
        )(send_invitation_signal_manager),
        sender=ExOAccountUser,
        weak=False)

from django import template
from django.conf import settings

register = template.Library()


@register.inclusion_tag(
    'network/details/invitation_status_tag.html',
    takes_context=True,
)
def registration_process_log(context, log_object):
    return {
        'log_text': log_object.frontend_message,
        'validation': None,
        'display_button': False,
        'invitation': None,
        'invitation_status': 'A',
        'display': log_object.display,
    }


@register.inclusion_tag(
    'network/details/invitation_status_tag.html',
    takes_context=True,
)
def invitation_status_tag(context, invitation):
    validation_status = invitation.invitation_related.content_object

    try:
        invitation_type_name = validation_status.validation.frontend_name
    except AttributeError:
        if not invitation.is_consultant_validation_type(invitation.invitation_related):
            if invitation.type == settings.INVITATION_TYPE_SIGNUP:
                invitation_type_name = 'Invitation to ExO Lever'

    display_button_resend = context.request.user.has_perm(
        settings.INVITATION_FULL_RESEND,
        invitation,
    )

    if invitation and hasattr(invitation, 'is_active'):
        display_button_resend = display_button_resend and not invitation.is_active

    pending_text = None
    if invitation.is_pending:
        if validation_status.is_agreement:
            pending_text = 'acceptance'

        elif validation_status.is_user or \
            validation_status.is_skill_assessment or \
                validation_status.is_profile:

            pending_text = 'filling it'

    return {
        'invitation_type_name': invitation_type_name,
        'validation': validation_status,
        'display_button': display_button_resend,
        'invitation': invitation,
        'invitation_status': invitation.status,
        'pending_text': pending_text,
        'display': True,
    }

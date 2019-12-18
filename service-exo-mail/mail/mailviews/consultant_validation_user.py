from django.conf import settings

from .base_consultant_validation import BaseConsultantValidationMailView


class ConsultantValidationUserMailView(BaseConsultantValidationMailView):
    template_name = 'mails/registration/invitation_user.html'
    subject = 'Invitation to Join ' + settings.BRAND_NAME + ' Community'
    section = 'registration'
    mandatory_mail_args = ['user_name', 'public_url', 'user_in_waiting_list']

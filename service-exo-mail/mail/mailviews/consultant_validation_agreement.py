from django.conf import settings

from .base_consultant_validation import BaseConsultantValidationMailView


class ConsultantValidationAgreementMailView(BaseConsultantValidationMailView):
    template_name = 'mails/registration/invitation_agreement.html'
    subject = 'Invite to Join ' + settings.BRAND_NAME + ' Community Reminder'
    section = 'registration'

from .base_consultant_validation import BaseConsultantValidationMailView


class ConsultantValidationApplicationMailView(BaseConsultantValidationMailView):
    template_name = 'mails/registration/invitation_application.html'
    subject = 'You have been invited to an Application'
    section = 'registration'

from .base_consultant_validation import BaseConsultantValidationMailView


class ConsultantValidationTestMailView(BaseConsultantValidationMailView):
    template_name = 'mails/registration/invitation_test.html'
    subject = 'You have been invited to complete this Test'
    section = 'registration'

from .base_consultant_validation import BaseConsultantValidationMailView


class ConsultantValidationOnBoardingMailView(BaseConsultantValidationMailView):
    template_name = 'mails/registration/invitation_on_boarding.html'
    subject = 'Please Complete your Basic Information'
    section = 'registration'

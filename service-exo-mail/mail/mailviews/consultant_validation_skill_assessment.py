from .base_consultant_validation import BaseConsultantValidationMailView


class ConsultantValidationSkillAssessmentMailView(BaseConsultantValidationMailView):
    template_name = 'mails/registration/invitation_skill_assessment.html'
    subject = 'ExO Skills Assessment'
    section = 'registration'

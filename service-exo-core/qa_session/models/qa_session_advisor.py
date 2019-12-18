from django.db import models

from model_utils.models import TimeStampedModel

from utils.models import CreatedByMixin


class QASessionAdvisor(CreatedByMixin, TimeStampedModel):
    consultant_project_role = models.ForeignKey(
        'relation.ConsultantProjectRole',
        related_name='qa_session_advisors',
        on_delete=models.CASCADE)

    qa_session = models.ForeignKey(
        'QASession',
        related_name='qa_session_advisors',
        on_delete=models.CASCADE)

    def __str__(self):
        return '{} - {}'.format(self.user, self.qa_session)

    @property
    def user(self):
        return self.consultant_project_role.consultant.user

    @property
    def need_job(self):
        return True

from django.conf import settings

from populate.populator.builder import Builder

from qa_session.models import QASession, QASessionAdvisor
from exo_role.models import ExORole


class QASessionBuilder(Builder):

    def create_object(self):
        qa_session = QASession.objects.create(
            name=self.data.get('name'),
            project=self.data.get('project'),
            start_at=self.data.get('starts'),
            end_at=self.data.get('ends'))

        for consultant in self.data.get('advisors'):
            c_project_role = consultant.roles.get(
                exo_role=ExORole.objects.get(code=settings.EXO_ROLE_CODE_ADVISOR),
                project=self.data.get('project')
            )

            QASessionAdvisor.objects.get_or_create(
                consultant_project_role=c_project_role,
                qa_session=qa_session,
            )

        return qa_session

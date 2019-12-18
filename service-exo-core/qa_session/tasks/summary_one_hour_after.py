from celery import Task

from ..models import QASession


class SummaryOneHourAfterTask(Task):
    name = 'SummaryOneHourAfterTask'
    ignore_result = True

    def run(self, *args, **kwargs):
        try:
            qa_session = QASession.objects.get(pk=kwargs.get('qa_session'))
        except QASession.DoesNotExist:
            return
        qa_session.send_participant_summary_email()

from celery import Task

from ..models import QASession


class ReminderOneHourBeforeTask(Task):
    name = 'ReminderOneHourBeforeTask'
    ignore_result = True

    def run(self, *args, **kwargs):
        try:
            qa_session = QASession.objects.get(pk=kwargs.get('qa_session'))
        except QASession.DoesNotExist:
            return
        qa_session.reminder_one_hour_before()

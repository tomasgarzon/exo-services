from django.utils import timezone

from celery.task.control import revoke

from utils.dates import increase_date, decrease_date
from utils.celery.search_tasks_scheduled import get_tasks_scheduled_by_app

from .conf import settings
from .tasks import (
    ReminderOneDayBeforeTask, ReminderOneHourBeforeTask,
    SummaryOneHourAfterTask)


def create_initial_reminder(instance):
    if instance.start_at < timezone.now():
        return
    scheduled_time = decrease_date(days=1, date=instance.start_at)
    ReminderOneDayBeforeTask().s(qa_session=instance.pk).apply_async(eta=scheduled_time)

    scheduled_time2 = decrease_date(seconds=3600, date=instance.start_at)
    ReminderOneHourBeforeTask().s(qa_session=instance.pk).apply_async(eta=scheduled_time2)

    scheduled_time5 = increase_date(seconds=3600, date=instance.end_at)
    SummaryOneHourAfterTask().s(qa_session=instance.pk).apply_async(eta=scheduled_time5)


def clear_reminder(instance):

    try:
        tasks_scheduled = get_tasks_scheduled_by_app(
            settings.QA_SESSION_APP_NAME)
    except AttributeError:
        # During testing time, inspect scheduled queue return None
        tasks_scheduled = []
    for task in tasks_scheduled:
        task_id = task.get('task_id')
        kwargs = eval(task.get('kwargs', '{}'))
        if kwargs.get('qa_session') == instance.id:
            revoke(task_id, terminate=True)

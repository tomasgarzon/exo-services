from .conf import settings

from celery.task.control import revoke

from utils.celery.search_tasks_scheduled import get_tasks_scheduled_by_app

from .tasks import (
    StartProjectTask,
    FinishProjectTask)


def create_status_updates(instance):
    if instance.start:
        scheduled_time = instance.start
        StartProjectTask().s(
            project_id=instance.pk,
            user_from_id=instance.created_by.pk,
        ).apply_async(eta=scheduled_time)
    if instance.end:
        scheduled_time = instance.end
        FinishProjectTask().s(
            project_id=instance.pk,
            user_from_id=instance.created_by.pk,
        ).apply_async(eta=scheduled_time)


def clear_updates(instance):

    try:
        tasks_scheduled = get_tasks_scheduled_by_app(
            settings.PROJECT_APP_NAME)
    except AttributeError:
        # During testing time, inspect scheduled queue return None
        tasks_scheduled = []
    for task in tasks_scheduled:
        task_id = task.get('task_id')
        kwargs = eval(task.get('kwargs', '{}'))
        if kwargs.get('project_id') == instance.id:
            revoke(task_id, terminate=True)

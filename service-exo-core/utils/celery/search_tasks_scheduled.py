from service.celery import app


def get_tasks_scheduled_by_name(name):
    inspect = app.control.inspect()
    tasks_scheduled = None
    for _, tasks in inspect.scheduled().items():
        for task in tasks:
            if task.get('request').get('name') == name:
                tasks_scheduled.append(
                    task.get('request'))
    return tasks_scheduled


def get_tasks_scheduled_by_kwargs(kwargs):
    inspect = app.control.inspect()
    tasks_scheduled = []
    for _, tasks in inspect.scheduled().items():
        for task in tasks:
            task_kwargs = eval(task.get('request').get('kwargs', '{}'))
            if task_kwargs == kwargs:
                tasks_scheduled.append(task.get('request'))
    return tasks_scheduled


def get_tasks_scheduled_by_app(app_name):
    inspect = app.control.inspect()
    tasks_scheduled = []
    for _, tasks in inspect.scheduled().items():
        for task in tasks:
            if task.get('request').get('name').startswith(app_name):
                tasks_scheduled.append(
                    task.get('request'))
    return tasks_scheduled

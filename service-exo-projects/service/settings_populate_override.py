from celery import current_app


current_app.conf.task_always_eager = True
current_app.conf.task_eager_propagates = True

from celery import current_app as app

from .update_user_microlearning import UpdateUserMicrolearningTask

app.tasks.register(UpdateUserMicrolearningTask())

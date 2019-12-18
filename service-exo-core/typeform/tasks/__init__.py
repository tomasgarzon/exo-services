from celery import current_app as app

from .user_typeform_responses import NewUserTypeformResponseMailTask


app.tasks.register(NewUserTypeformResponseMailTask())

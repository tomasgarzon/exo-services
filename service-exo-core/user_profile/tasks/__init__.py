from celery import current_app as app

from .new_conversation_user import NewConversationUserTask


app.tasks.register(NewConversationUserTask())

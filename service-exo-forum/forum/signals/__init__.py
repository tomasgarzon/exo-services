from django.apps import apps
from django.db.models.signals import post_save as post_save_signal
from django.db.models.signals import post_delete as post_delete_signal

from exo_mentions.registry import register

from .post_save import new_topic_post_save_handler, new_answer_post_save_handler
from .post_delete import answer_post_delete_handler
from .post_mention import (
    post_detect_mention_callback,
    answer_detect_mention_callback,
)


def setup_signals():
    Post = apps.get_model(app_label='forum', model_name='Post')
    Answer = apps.get_model(app_label='forum', model_name='Answer')

    post_save_signal.connect(new_topic_post_save_handler, sender=Post)
    post_save_signal.connect(new_answer_post_save_handler, sender=Answer)

    post_delete_signal.connect(answer_post_delete_handler, sender=Answer)


def setup_mentions():
    Post = apps.get_model(app_label='forum', model_name='Post')
    Answer = apps.get_model(app_label='forum', model_name='Answer')
    register(model=Post, field='description', callback=post_detect_mention_callback)
    register(model=Answer, field='comment', callback=answer_detect_mention_callback)

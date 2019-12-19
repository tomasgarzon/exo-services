from actstream.models import followers
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from celery import Task

from circles.models import Circle
from utils import notifications
from utils.mail import handlers

from ..api.serializers.post import PostDetailSerializer, PostDetailSwarmSerializer
from ..helpers import get_topic_by_object
from ..models import Post, Answer
from ..models.mails.mention import PostMentionCreated, AnswerMentionCreated


class PostSendEmailCreatedTask(Task):
    name = 'PostSendEmailCreatedTask'
    ignore_result = True

    def run(self, post_pk, *args, **kwargs):
        post = get_object_or_404(Post, pk=post_pk)

        if post.is_circle:
            post.new_topic_created()
        elif post.is_project:
            post.new_question_created()
        elif post.is_announcement:
            post.new_announcement_created()


class PostSendEmailReplyTask(Task):
    name = 'PostSendEmailReplyTask'
    ignore_result = True

    def run(self, post_pk, answer_pk, *args, **kwargs):
        post = get_object_or_404(Post, pk=post_pk)
        answer = get_object_or_404(Answer, pk=answer_pk)

        if post.is_announcement:
            post.new_announcement_reply(answer)
        elif post.is_project:
            post.new_question_reply(answer)


class NotifyPostChangeTask(Task):
    name = 'NotifyPostChangeTask'

    def run(self, *args, **kwargs):
        try:
            post = Post.objects.get(pk=kwargs.get('post_pk'))
        except Post.DoesNotExist:
            return
        action = kwargs.get('action')
        context = {}

        if post.qa_session:
            qa_team = post.qa_sessions.first()
            following = qa_team.get_available_users(search='')
            context['project'] = post.project
        elif post.is_project:
            following = list(post.team.get_granted_users())
            circle = Circle.objects.get(slug='ecosystem')
            following = list(set(following + followers(circle)))
            context['project'] = post.project
        elif post.circle:
            following = followers(post.circle)
        elif post.is_announcement:
            following = followers(Circle.objects.get(slug='ecosystem'))
        else:
            following = []

        for follower in following:
            if follower != post.created_by:
                class UserReq:
                    user = follower
                context['request'] = UserReq
                if post.qa_session:
                    serializer = PostDetailSwarmSerializer(post, context=context)
                else:
                    serializer = PostDetailSerializer(post, context=context)
                notifications.send_notifications(
                    get_topic_by_object(post),
                    action,
                    post.__class__.__name__.lower(),
                    follower.uuid,
                    serializer.data)


class PostMentionSendEmailTask(Task):
    name = 'PostMentionSendEmailTask'
    ignore_result = True

    def run(self, user_metioned_pk, post_pk, *args, **kwargs):
        user = get_user_model()
        user_mentioned = get_object_or_404(user, pk=user_metioned_pk)
        post = get_object_or_404(Post, pk=post_pk)
        email_template_name = 'post_mention'
        mail_kwargs = PostMentionCreated(post).get_data(user_mentioned)
        handlers.mail_handler.send_mail(email_template_name, **mail_kwargs)


class AnswerMentionSendEmailTask(Task):
    name = 'AnswerMentionSendEmailTask'
    ignore_result = True

    def run(self, user_metioned_pk, post_pk, answer_pk, *args, **kwargs):
        user = get_user_model()
        user_mentioned = get_object_or_404(user, pk=user_metioned_pk)
        answer = get_object_or_404(Answer, pk=answer_pk)
        post = get_object_or_404(Post, pk=post_pk)
        email_template_name = 'post_mention_answer'
        mail_kwargs = AnswerMentionCreated(post, answer).get_data(user_mentioned)
        handlers.mail_handler.send_mail(email_template_name, **mail_kwargs)

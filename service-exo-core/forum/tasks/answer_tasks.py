from actstream.models import followers
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from celery import Task

from utils import notifications

from ..api.serializers.answer import AnswerPostSerializer, AnswerPostSwarmSerializer
from ..helpers import get_topic_by_object
from ..models import Answer, Post


class PostAnswerRatingTask(Task):
    name = 'PostAnswerRatingTask'
    ignore_result = True

    def run(self, answer_pk, rating, *args, **kwargs):
        answer = get_object_or_404(Answer, pk=answer_pk)
        answer.notify_answer_rating(rating)


class MarkAnswerAsReadTask(Task):
    name = 'MarkAnswerAsReadTask'

    def run(self, *args, **kwargs):
        answers = Answer.objects.filter(pk__in=kwargs.get('answer_pks', []))
        post = Post.objects.get(pk=kwargs.get('post_pk'))
        user = get_user_model().objects.get(pk=kwargs.get('user_pk'))
        post.see(user)

        for answer in answers:
            answer.see(user)


class NotifyAnswerChangeTask(Task):
    name = 'NotifyAnswerChangeTask'

    def run(self, *args, **kwargs):
        try:
            answer = Answer.objects.get(pk=kwargs.get('answer_pk'))
        except Answer.DoesNotExist:
            return
        action = kwargs.get('action')
        post = answer.post
        context = {}

        if post.qa_session:
            qa_team = post.qa_sessions.first()
            following = qa_team.get_available_users(search='')
            context['project'] = post.project
            serializer = AnswerPostSwarmSerializer(answer, context=context)
        else:
            if post.is_project:
                context['project'] = post.project
            following = followers(post)
            serializer = AnswerPostSerializer(answer, context=context)

        for follower in following:
            if follower != answer.created_by:
                class UserReq:
                    user = follower
                context['request'] = UserReq
                notifications.send_notifications(
                    get_topic_by_object(answer),
                    action,
                    answer.__class__.__name__.lower(),
                    follower.uuid,
                    serializer.data)

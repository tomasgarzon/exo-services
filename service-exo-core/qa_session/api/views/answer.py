from django.http import Http404
from rest_framework import mixins

from forum.api.serializers.answer import AnswerPostSerializer
from forum.models import Answer, Post
from forum.tasks.answer_tasks import MarkAnswerAsReadTask

from .mixins import QASessionGenericViewMixin, BasicPageNumberPagination


class QASessionAnswerViewSet(
        mixins.ListModelMixin,
        QASessionGenericViewMixin):
    queryset = Answer.objects.all()
    pagination_class = BasicPageNumberPagination
    serializers = {
        'default': AnswerPostSerializer
    }

    def get_queryset(self):
        user = self.request.user
        question = Post.objects.get(
            pk=self.kwargs.get('question_id', None))
        if not question.can_see(user):
            raise Http404
        return self.queryset.filter(post=question)

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        MarkAnswerAsReadTask().s(
            answer_pks=[item['pk'] for item in response.data['results']],
            user_pk=self.request.user.pk,
            post_pk=self.kwargs.get('question_id', None),
        ).apply_async()
        return response

from actstream.models import Follow
from django.db.models import QuerySet, Q, Subquery, IntegerField
from django.contrib.contenttypes.models import ContentType
from django.db.models.functions import Cast

from utils.descriptors import CustomFilterDescriptorMixin
from ..conf import settings


class PostQuerySet(CustomFilterDescriptorMixin, QuerySet):

    FILTER_DESCRIPTORS = [
        {
            'field': '_type',
            'options': settings.FORUM_POST_CH_TYPE,
        },
        {
            'field': 'status',
            'options': settings.FORUM_CH_POST_STATUS,
        },
    ]

    def filter_by_circle(self, circle):
        ct = ContentType.objects.get_for_model(circle)
        return self.filter(
            content_type=ct,
            object_id=circle.id)

    def filter_by_circles(self, circles):
        if not circles:
            return self.none()
        ct = ContentType.objects.get_for_model(circles[0])
        return self.filter(
            content_type=ct,
            object_id__in=[c.pk for c in circles])

    def filter_by__type(self, post_type):
        return self.filter(_type=post_type)

    def filter_by_projects(self, project_list):
        project = project_list.first()
        if not project:
            return []
        ct = ContentType.objects.get_for_model(project)
        return self.filter(
            content_type=ct,
            object_id__in=project_list.values_list('id', flat=True))

    def filter_by_qa_session_team(self, qa_session, team):
        qa_session_team = qa_session.teams.filter(team=team).first()
        if not qa_session_team:
            return self.none()
        ct = ContentType.objects.get_for_model(qa_session_team)
        return self.filter(
            content_type=ct,
            object_id=qa_session_team.id)

    def filter_by_qa_session(self, qa_session):
        qa_session_teams = qa_session.teams.all()
        ct = ContentType.objects.get_for_model(qa_session_teams[0])
        return self.filter(
            content_type=ct,
            object_id__in=qa_session_teams.values_list('id', flat=True))

    def filter_by_status(self, status):
        if type(status) == list:
            q_filter = Q(status__in=status)
        else:
            q_filter = Q(status=status)

        return self.filter(q_filter).distinct()

    def filter_by_search(self, search):
        cond1 = Q(title__icontains=search)
        cond2 = Q(description__icontains=search)
        return self.filter(cond1 | cond2).distinct()

    def filter_by_user_subscribed(self, user):
        query = Follow.objects.following_qs(
            user, self.model
        ).annotate(as_integer=Cast('object_id', IntegerField()))

        return self.filter(
            id__in=Subquery(query.values('as_integer')))

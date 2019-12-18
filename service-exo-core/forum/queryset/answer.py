from django.db.models import QuerySet, Q
from django.contrib.contenttypes.models import ContentType

from utils.descriptors import CustomFilterDescriptorMixin

from ..conf import settings


class AnswerQuerySet(CustomFilterDescriptorMixin, QuerySet):
    FILTER_DESCRIPTORS = [
        {
            'field': 'status',
            'options': settings.FORUM_CH_POST_STATUS,
        },
    ]

    def filter_by_circle(self, circle):
        ct = ContentType.objects.get_for_model(circle)
        return self.filter(
            post__content_type=ct,
            post__object_id=circle.id)

    def filter_by_post_type(self, post_type):
        return self.filter(post___type=post_type)

    def filter_by_projects(self, project_list):
        project = project_list.first()
        if not project:
            return []
        ct = ContentType.objects.get_for_model(project)
        return self.filter(
            post__content_type=ct,
            post__object_id__in=project_list.values_list('id', flat=True))

    def filter_by_status(self, status):
        if type(status) == list:
            q_filter = Q(status__in=status)
        else:
            q_filter = Q(status=status)

        return self.filter(q_filter).distinct()

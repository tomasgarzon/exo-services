from guardian.models import UserObjectPermission

from django.db.models import Q, IntegerField
from django.db.models.functions import Cast
from django.contrib.contenttypes.models import ContentType

from project.models import Project


def get_project_for_user(user):
    if user.is_superuser:
        return Project.objects.all()
    q1 = Q(created_by=user)
    project_id = UserObjectPermission.objects.annotate(
        as_integer=Cast('object_pk', IntegerField())
    ).filter(
        user=user,
        object_pk__isnull=False,
        content_type=ContentType.objects.get_for_model(Project)).values_list(
            'as_integer', flat=True)
    q2 = Q(id__in=project_id)
    return Project.objects.filter(q1 | q2)

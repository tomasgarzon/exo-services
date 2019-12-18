from django.db.models import Q

from project.queryset.project import BaseProjectQuerySet
from permissions.objects import get_team_for_user

from ..conf import settings


class TeamQuerySet(BaseProjectQuerySet):
    _fields_from_form = {}

    def filter_by_project(self, project):
        return self.filter(sprint=project.sprint)

    def filter_by_user(self, project, user):
        return get_team_for_user(project, user)

    def filter_by_coach(self, consultant):
        return self.filter(coach=consultant)

    def filter_by_search(self, search):
        stream_reverse = []
        for k, v in settings.PROJECT_STREAM_CH_TYPE:
            if v.lower().find(search.lower()) >= 0:
                stream_reverse.append(k)

        return Q(name__icontains=search) | Q(stream__in=stream_reverse)

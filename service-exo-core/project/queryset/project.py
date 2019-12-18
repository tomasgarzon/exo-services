from django.utils import timezone
from django.db.models import F, Case, When, Max, Q

from guardian.shortcuts import get_objects_for_user

from utils.queryset import QuerySetFilterComplexMixin

from ..conf import settings


class BaseProjectQuerySet(QuerySetFilterComplexMixin):
    _fields_from_form = {
        'search': [
            'name__icontains',
            'customer__name__icontains',
        ],
    }

    def filter_by_user(self, user):
        project_ids = get_objects_for_user(user, settings.PROJECT_FULL_VIEW).values_list('id', flat=True)
        return self.filter(id__in=project_ids)

    def filter_by_type(self, project_type):
        key = '{}__isnull'.format(project_type)
        kwargs = {key: False}
        return self.filter(**kwargs)

    def filter_by_user_or_organization(self, user):
        project_ids = get_objects_for_user(
            user, settings.PROJECT_FULL_VIEW).values_list('id', flat=True)

        organizations = user.organizations_roles.values_list('organization', flat=True)
        query_organization = Q(
            internal_organization__in=organizations)
        query = Q(id__in=project_ids)
        return self.filter(query_organization | query)


class ProjectQuerySet(BaseProjectQuerySet):

    def multiple(self):
        return self.count() > 1

    def actives(self, _datetime=None):
        """
            Projects that are HAPPENING at this date
        """
        if not _datetime:
            _datetime = timezone.now()
        has_end = When(end__isnull=False, then=F('end'))
        step_end = When(
            end__isnull=True,
            then=Max(F('steps__end')),
        )
        return self.annotate(
            new_end=Case(
                has_end, step_end,
            ),
        ).filter(start__lte=_datetime, new_end__gte=_datetime)

    def finished(self, _date=None):
        """
            Projects finished UNTIL this date or today
        """
        if not _date:
            _date = timezone.now().date()

        has_end = When(end__isnull=False, then=F('end'))
        step_end = When(
            end__isnull=True,
            then=Max(F('steps__end')),
        )

        return self.annotate(
            date_ended=Case(
                has_end, step_end,
            ),
        ).filter(date_ended__date__lte=_date)

    def exclude_draft(self):
        return self.exclude(status=settings.PROJECT_CH_PROJECT_STATUS_DRAFT)

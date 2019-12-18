from django.db import models
from django.utils import timezone
from django.db.models import F, Case, When, Max, Value, IntegerField

from ..conf import settings


class ProjectQuerySet(models.QuerySet):
    FILTER_DESCRIPTORS = [{
        'field': 'content_template',
        'options': settings.PROJECT_CH_PROJECT_TEMPLATE,
    }, {
        'field': 'status',
        'options': settings.PROJECT_CH_STATUS,
    }]

    def filter_by_uuid(self, uuid):
        return self.filter(uuid=uuid)

    def filter_by_template(self, content_template):
        return self.filter(content_template=content_template)

    def filter_by_status(self, status):
        return self.filter(status=status)

    def actives(self, _datetime=None):
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

    def exclude_training(self):
        return self.filter(training=False)

    def exclude_draft(self):
        return self.exclude(status=settings.PROJECT_CH_STATUS_DRAFT)

    def not_removed(self):
        return self.exclude(status=settings.PROJECT_CH_STATUS_REMOVED)

    def annotate_status_order(self):
        cases = [
            When(status=status, then=Value(index))
            for index, (status, _) in enumerate(settings.PROJECT_CH_STATUS)]

        return self.annotate(
            status_order=Case(
                *cases,
                default=Value(5),
                output_field=IntegerField(),
            )
        )

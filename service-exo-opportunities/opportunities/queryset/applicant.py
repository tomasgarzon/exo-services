from django.db.models import QuerySet, Q, Value, When, Case, IntegerField
from django.contrib.auth import get_user_model

from utils.descriptors import CustomFilterDescriptorMixin

from ..conf import settings


class ApplicantQuerySet(CustomFilterDescriptorMixin, QuerySet):
    FILTER_DESCRIPTORS = [{
        'field': 'status',
        'options': settings.OPPORTUNITIES_CH_APPLICANT_STATUS,
    }]

    def filter_by_user(self, user):
        return self.filter(user=user)

    def filter_by_status(self, status):
        if type(status) == list:
            q_filter = Q(status__in=status)
        else:
            q_filter = Q(status=status)

        return self.filter(q_filter).distinct()

    def get_statuses_selected(self):
        return [
            settings.OPPORTUNITIES_CH_APPLICANT_SELECTED,
            settings.OPPORTUNITIES_CH_APPLICANT_COMPLETED,
            settings.OPPORTUNITIES_CH_APPLICANT_FEEDBACK_REQUESTER,
            settings.OPPORTUNITIES_CH_APPLICANT_FEEDBACK_APP,
            settings.OPPORTUNITIES_CH_APPLICANT_FEEDBACK_READY
        ]

    def filter_by_advisor_selected(self):
        return self.filter_by_status(
            status=self.get_statuses_selected(),
        )

    def order_by_status(self):
        SELECTED_AND_COMPLETED = self.get_statuses_selected()
        return self.annotate(status_order=Case(
            When(
                status__in=SELECTED_AND_COMPLETED,
                then=Value(1)),
            When(
                status=settings.OPPORTUNITIES_CH_APPLICANT_REQUESTED,
                then=Value(2)),
            When(
                status=settings.OPPORTUNITIES_CH_APPLICANT_REJECTED,
                then=Value(3)),
            output_field=IntegerField()
        )).order_by('status_order', '-modified')

    def pending_applicants(self):
        status_applicants = [
            settings.OPPORTUNITIES_CH_APPLICANT_REQUESTED,
        ]
        return self.filter_by_status(status=status_applicants)

    def users(self):
        user_ids = self.values_list('user', flat=True)
        return get_user_model().objects.filter(id__in=user_ids)

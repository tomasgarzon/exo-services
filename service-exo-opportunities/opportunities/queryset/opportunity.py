from django.db import models
from django.db.models.functions import Greatest
from django.db.models import Max, Q

from functools import reduce

from utils.descriptors import CustomFilterDescriptorMixin

from ..conf import settings


class OpportunityQuerySet(
        CustomFilterDescriptorMixin, models.QuerySet):

    FILTER_DESCRIPTORS = [
        {
            'field': '_status',
            'options': settings.OPPORTUNITIES_CH_STATUS,
        }, {
            'field': 'target',
            'options': settings.OPPORTUNITIES_CH_TARGET,
        },
    ]

    def filter_by__status(self, status):
        if type(status) == list:
            q_filter = Q(_status__in=status)
        else:
            q_filter = Q(_status=status)

        return self.filter(q_filter)

    def filter_by_roles(self, roles):
        if type(roles) == list:
            q_filter = Q(exo_role__code__in=roles)
        else:
            q_filter = Q(exo_role__code=roles)

        return self.filter(q_filter)

    def filter_by_target(self, target):
        return self.filter(target=target)

    def not_draft(self):
        return self.exclude(_status=settings.OPPORTUNITIES_CH_DRAFT)

    def not_removed(self):
        return self.exclude(_status=settings.OPPORTUNITIES_CH_REMOVED)

    def users_can_apply(self, user):
        q1 = models.Q(
            target=settings.OPPORTUNITIES_CH_TARGET_OPEN,
            _status=settings.OPPORTUNITIES_CH_REQUESTED,
        )
        q2 = models.Q(
            target=settings.OPPORTUNITIES_CH_TARGET_FIXED,
            applicants=user,
            _status=settings.OPPORTUNITIES_CH_REQUESTED,
        )
        return self.filter(q1 | q2)

    def users_can_see(self, user):
        q1 = models.Q(
            target=settings.OPPORTUNITIES_CH_TARGET_OPEN,
        )
        q2 = models.Q(
            target=settings.OPPORTUNITIES_CH_TARGET_FIXED,
            applicants=user,
        )
        return self.filter(q1 | q2)

    def order_by_date(self):
        return self.annotate(
            max_status=Max('history__modified'),
            max_app_status=Max('applicants_info__history__modified'),
        ).annotate(
            max_date=Greatest(
                'max_status', 'max_app_status'
            ),
        ).order_by('-max_date', 'pk')

    def filter_by_user(self, user, pk=None, status=None):
        all_user_opportunities = Q()

        user_available_opportunities = reduce(
            lambda x, y: x + y,
            [
                self._level_high_conditions(user),
                self._level_medium_conditions(user),
                self._level_low_conditions(user),
            ]
        )
        for query in user_available_opportunities:
            all_user_opportunities |= query
        return self.filter(
            all_user_opportunities,
            Q(pk=pk) if pk else Q(),
            Q(status=status) if status else Q(),
        )

    def _level_high_conditions(self, user):
        """
        Filter for:
            - TARGET `Opportunities` instances
        """
        opportunity_status = [
            settings.OPPORTUNITIES_CH_REQUESTED,
            settings.OPPORTUNITIES_CH_CLOSED,
        ]

        return [
            Q(target=settings.OPPORTUNITIES_CH_TARGET_FIXED) & Q(
                _status__in=opportunity_status) & Q(
                users_tagged__user=user)
        ]

    def _level_medium_conditions(self, user):
        """
        Filter for:
            - OPEN `Opportunity` instances
        """
        open_opportunities_with_no_interaction = (
            Q(target=settings.OPPORTUNITIES_CH_TARGET_OPEN) & Q(
                _status__in=[
                    settings.OPPORTUNITIES_CH_REQUESTED,
                ]) & ~Q(applicants_info__user=user)
        )
        open_opportunities_with_user_interaction = (
            Q(target=settings.OPPORTUNITIES_CH_TARGET_OPEN) & Q(
                _status__in=[
                    settings.OPPORTUNITIES_CH_REQUESTED,
                    settings.OPPORTUNITIES_CH_CLOSED,
                ]) & Q(
                applicants_info__user=user,
                applicants_info__status__in=[
                    settings.OPPORTUNITIES_CH_APPLICANT_REQUESTED,
                    settings.OPPORTUNITIES_CH_APPLICANT_SELECTED,
                    settings.OPPORTUNITIES_CH_APPLICANT_COMPLETED,
                    settings.OPPORTUNITIES_CH_APPLICANT_FEEDBACK_REQUESTER,
                    settings.OPPORTUNITIES_CH_APPLICANT_FEEDBACK_APP,
                    settings.OPPORTUNITIES_CH_APPLICANT_FEEDBACK_READY])
        )

        return [
            open_opportunities_with_no_interaction,
            open_opportunities_with_user_interaction,
        ]

    def _level_low_conditions(self, user):
        """
        Filter for:
            - OPEN `Opportunity` instances removed with `Consultant` Interaction
            - TARGET `Opportunity` instances removed for this `Consultant`
        """
        applicant_status_not_done = [
            settings.OPPORTUNITIES_CH_APPLICANT_REJECTED,
        ]

        all_opportunities_cancelled_by_user_or_done_by_others = (
            Q(applicants_info__user=user,
              applicants_info__status__in=applicant_status_not_done))

        return [
            all_opportunities_cancelled_by_user_or_done_by_others,
        ]

    def filter_by_applicants_assigned(self):
        return self.filter(
            applicants_info__status=settings.OPPORTUNITIES_CH_APPLICANT_SELECTED)

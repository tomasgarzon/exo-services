from django.db import models

from ..queryset.consultant_exo_activity import ConsultantExOActivityQuerySet


class ConsultantExOActivityManager(models.Manager):

    queryset_class = ConsultantExOActivityQuerySet
    use_for_related_fields = True
    use_in_migrations = True

    def get_queryset(self):
        return self.queryset_class(self.model, using=self._db)

    def disabled_or_pending(self):
        return self.get_queryset().disabled_or_pending()

    def actives(self):
        return self.get_queryset().actives()

    def disabled(self):
        return self.get_queryset().disabled()

    def pending(self):
        return self.get_queryset().pending()

    def filter_by_consultant(self, consultant):
        return self.get_queryset().filter_by_consultant(consultant)

    def disable_unmarked_consultant_activities(
        self,
        consultant,
        user_selected_activities,
    ):

        consultant_activity_to_disable = self.filter_by_consultant(
            consultant,
        ).exclude(exo_activity__in=user_selected_activities)

        for consultant_activity in consultant_activity_to_disable:
            consultant_activity.disable()

    def update_from_values(self, consultant_profile, exo_activities):

        consultant = consultant_profile.consultant

        for exo_activity in exo_activities:
            consultant_activity, created = self.get_or_create(
                consultant_profile=consultant_profile,
                exo_activity=exo_activity,
            )
            if consultant_activity.should_be_reactivated(created):
                consultant_activity.enable()

        self.disable_unmarked_consultant_activities(
            consultant=consultant,
            user_selected_activities=exo_activities,
        )

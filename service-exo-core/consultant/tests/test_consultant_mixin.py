from django.conf import settings

from exo_activity.models import ExOActivity


class TestConsultantMixin:

    def enable_advising_for_consultant(self, consultant):
        exo_advising = ExOActivity.objects.get(
            code=settings.EXO_ACTIVITY_CH_ACTIVITY_ADVISING)
        exo_activity, _ = consultant.exo_profile.exo_activities.get_or_create(
            exo_activity=exo_advising)

        return exo_activity

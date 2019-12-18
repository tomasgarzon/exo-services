from django.db.models import Manager

from actstream.actions import follow

from utils.descriptors import CustomFilterDescriptorMixin

from ..conf import settings
from ..models.answer import Answer
from ..signals_define import opportunity_new_applicant
from ..queryset.applicant import ApplicantQuerySet


class ApplicantManager(CustomFilterDescriptorMixin, Manager):
    use_for_related_fields = True
    use_in_migrations = True
    queryset_class = ApplicantQuerySet
    FILTER_DESCRIPTORS = [{
        'field': 'status',
        'options': settings.OPPORTUNITIES_CH_APPLICANT_STATUS,
    }]

    def get_queryset(self):
        return self.queryset_class(self.model, using=self._db)

    def filter_by_user(self, user):
        return self.get_queryset().filter_by_user(user)

    def filter_by_status(self, status):
        return self.get_queryset().filter_by_status(status)

    def pending_applicants(self):
        return self.get_queryset().pending_applicants()

    def filter_by_advisor_selected(self):
        return self.get_queryset().filter_by_advisor_selected()

    def create_open_applicant(
            self, user_from, user,
            opportunity, summary, questions_extra_info=None,
            budget=None, answers=[]):

        applicant = self.create(
            opportunity=opportunity,
            user=user,
            summary=summary,
            questions_extra_info=questions_extra_info,
            budget=budget,
            status=settings.OPPORTUNITIES_CH_APPLICANT_REQUESTED,
        )
        for answer in answers:
            if answer.get('question').is_boolean:
                answer['response'] = answer['response'].capitalize()
            Answer.objects.create(applicant=applicant, **answer)

        follow(user, opportunity)
        opportunity_new_applicant.send(
            sender=applicant.__class__,
            opportunity=opportunity,
            applicant=applicant)
        return applicant

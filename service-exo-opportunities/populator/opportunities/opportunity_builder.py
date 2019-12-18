from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.conf import settings

from populate.populator.builder import Builder
from keywords.models import Keyword
from exo_role.models import ExORole, CertificationRole

from opportunities.models import (
    Opportunity, Applicant, Question)
from opportunities.faker_factories.question import FakeQuestionFactory

User = get_user_model()


class OpportunityBuilder(Builder):

    def create_object(self):
        opp = self.create_opportunity(
            title=self.data.get('title'),
            description=self.data.get('description'),
            keywords=self.data.get('keywords'),
            mode=self.data.get('mode'),
            location=self.data.get('location'),
            location_url=self.data.get('location_url'),
            place_id=self.data.get('place_id'),
            start_date=self.data.get('start_date'),
            deadline_date=self.data.get('deadline_date'),
            duration_unity=self.data.get('duration_unity'),
            duration_value=self.data.get('duration_value'),
            exo_role=self.data.get('exo_role'),
            certification_required=self.data.get('certification_required'),
            entity=self.data.get('entity'),
            created_by=self.data.get('created_by'),
            budget=self.data.get('budget'),
            virtual_budget=self.data.get('virtual_budget'),
            budget_currency=self.data.get('budget_currency'),
            created=self.data.get('created'),
            num_positions=self.data.get('num_positions'),
            uuid=self.data.get('uuid'),
            target=self.data.get('target', settings.OPPORTUNITIES_CH_TARGET_OPEN),
            users_tagged=self.data.get('users_tagged', []),
            group=self.data.get('group'),
        )
        for question_data in self.data.get('questions', []):
            try:
                FakeQuestionFactory(opportunity=opp, **question_data)
            except IntegrityError:
                pass

        self.create_applicants(
            opportunity=opp,
            applicants=self.data.get('applicants', []),
            user_from=self.data.get('assigned_by'))

        if self.data.get('status') in settings.OPPORTUNITIES_ADMIN_ACTIONS:
            if self.data.get('status') == self.CH_CLOSED:
                opp.close(self.data.get('assigned_by'))

        return opp

    def create_single_applicant(self, user_from, user, opportunity, data):
        app = Applicant.objects.create_open_applicant(
            user_from=user,
            user=user,
            opportunity=opportunity,
            summary=data.get('summary'),
            questions_extra_info=data.get('questions_extra_info'),
            budget=data.get('budget'),
            answers=data.get('answers', []),
        )
        return app

    def create_applicants(self, opportunity, applicants, user_from):
        for appl in applicants:
            user = appl.get('user')
            for index, _ in enumerate(appl.get('answers', [])):
                appl['answers'][index]['question'] = Question.objects.get(
                    pk=appl.get('answers')[index].get('question')
                )

            app = self.create_single_applicant(user, user, opportunity, appl)

            if appl.get('status') == 'Rejected':
                app.mark_as_rejected(user_from)
            else:
                sow_data = appl.get('sow', {})
                app.mark_as_selected(user_from, **sow_data)

                if appl.get('status') in ['Completed', 'FeedbackDone', 'FeedbackReady']:
                    app.set_completed()

                    for feedback in appl.get('feedbacks', []):
                        user_from = feedback.pop('user')
                        app.give_feedback(user_from=user_from, **feedback)

                if appl.get('status') == 'FeedbackReady':
                    app.set_feedback_expired()

        return opportunity

    def create_opportunity(self, *args, **kwargs):
        keywords = kwargs.pop('keywords', [])
        keywords = [
            Keyword.objects.get_or_create(name=k)[0] for k in keywords]
        kwargs['keywords'] = keywords

        exo_role = kwargs.pop('exo_role', None)
        if exo_role:
            kwargs['exo_role'] = ExORole.objects.get(code=exo_role)

        certification_required = kwargs.pop('certification_required', None)
        if certification_required:
            kwargs['certification_required'] = CertificationRole.objects.get(
                code=certification_required)

        budget_currency = kwargs.pop('budget_currency', None)
        if budget_currency:
            budget_currency = next(
                str(curr[0])
                for curr in settings.OPPORTUNITIES_CH_CURRENCY
                if str(curr[1]) == budget_currency
            )
        kwargs['budget_currency'] = budget_currency
        budgets = []
        if kwargs.get('budget'):
            budgets.append(
                {
                    'budget': kwargs.get('budget'),
                    'currency': kwargs.get('budget_currency')})
        if kwargs.get('virtual_budget'):
            budgets.append(
                {
                    'budget': kwargs.get('virtual_budget').__str__(),
                    'currency': kwargs.get('virtual_budget_currency', settings.OPPORTUNITIES_CH_CURRENCY_EXOS)})
        kwargs['budgets'] = budgets
        group = kwargs.pop('group', None)
        if group:
            opportunity = Opportunity.objects.create_opportunity_in_group(
                user_from=kwargs.pop('created_by'),
                group=group,
                **kwargs)
        else:
            opportunity = Opportunity.objects.create_opportunity(
                user_from=kwargs.pop('created_by'),
                **kwargs)

        created = kwargs.get('created')
        if created:
            self._update_created_date(opportunity, created)

        return opportunity

    def _update_created_date(self, opportunity, created):
        Opportunity.objects.filter(
            pk=opportunity.id).update(created=created)

    def update_history(self, opportunity, when):
        last = opportunity.history.last()
        last.created = when
        last.save(update_fields=['created'])

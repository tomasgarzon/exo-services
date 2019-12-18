from django.db import models

from utils.descriptors import CustomFilterDescriptorMixin
from files.models import UploadedFile

from ..conf import settings
from ..models.question import Question
from ..queryset.opportunity import OpportunityQuerySet
from ..signals_define import opportunity_post_edited


class OpportunityManager(CustomFilterDescriptorMixin, models.Manager):
    use_for_related_fields = True
    use_in_migrations = True
    queryset_class = OpportunityQuerySet

    FILTER_DESCRIPTORS = [
        {
            'field': '_status',
            'options': settings.OPPORTUNITIES_CH_STATUS,
        }, {
            'field': 'target',
            'options': settings.OPPORTUNITIES_CH_TARGET,
        },
    ]

    def get_queryset(self):
        queryset = self.queryset_class(
            self.model, using=self._db,
        ).order_by('-modified')
        return queryset.distinct()

    def filter_by__status(self, status):
        return self.get_queryset().filter_by__status(status)

    def filter_by_roles(self, roles):
        return self.get_queryset().filter_by_roles(roles)

    def filter_by_applicants_assigned(self):
        return self.get_queryset().filter_by_applicants_assigned()

    def filter_by_target(self, target):
        return self.get_queryset().filter_by_target(target)

    def not_draft(self):
        return self.get_queryset().not_draft()

    def users_can_apply(self, consultant):
        return self.get_queryset().users_can_apply(consultant)

    def users_can_see(self, consultant):
        return self.get_queryset().users_can_see(consultant)

    def filter_by_user(self, user, pk=None, status=None):
        return self.get_queryset().filter_by_user(
            user=user,
            pk=pk,
            status=status,
        )

    def update_budget(self, opportunity, budgets):
        data = {
            'budget': None,
            'budget_currency': None,
            'virtual_budget': None,
            'virtual_budget_curency': None
        }
        for value in budgets:
            budget = value['budget']
            currency = value['currency']
            if currency in dict(settings.OPPORTUNITIES_CH_CURRENCY):
                data['budget'] = budget
                data['budget_currency'] = currency
            elif currency in dict(settings.OPPORTUNITIES_CH_VIRTUAL_CURRENCY):
                data['virtual_budget'] = budget
                data['virtual_budget_currency'] = currency
        for key, value in data.items():
            setattr(opportunity, key, value)

    def update_files(self, opportunity, files):
        for file in opportunity.files.all():
            remove = True
            for new_file in files:
                if new_file.get('url') == file.url:
                    remove = False
                    break
            if remove:
                file.delete()

        for data in files:
            UploadedFile.create(
                created_by=opportunity.created_by,
                filename=data.get('filename'),
                mimetype=data.get('mimetype'),
                filestack_url=data.get('url'),
                filestack_status=data.get('filestack_status'),
                related_to=opportunity)

    def _create_questions(self, opportunity, questions):
        for question_data in questions:
            Question.objects.create(opportunity=opportunity, **question_data)

    def _create_users_tagged(self, opportunity, users_tagged):
        for user in users_tagged:
            opportunity.users_tagged.create(user=user)

    def update_questions(self, opportunity, questions):
        for question in questions:
            question_id = question.get('id')
            if question_id:
                Question.objects.update_or_create(
                    id=question_id,
                    opportunity=opportunity,
                    defaults={
                        'title': question['title']})
            else:
                Question.objects.create(
                    opportunity=opportunity,
                    title=question['title'])
        questions_removed = Question.objects.filter(
            opportunity=opportunity).exclude(
            title__in=list(
                filter(
                    lambda x: x is not None,
                    map(lambda x: x.get('title'), questions))
            )
        )
        questions_removed.delete()

    def create_opportunity_in_group(self, user_from, group, **kwargs):
        new_data = kwargs.copy()
        new_data['entity'] = group.entity
        new_data['exo_role'] = group.exo_role
        new_data['duration_unity'] = group.duration_unity
        new_data['duration_value'] = group.duration_value
        new_data['budgets'] = group.budgets
        return self.create_opportunity(
            user_from, group=group, **new_data)

    def create_opportunity(self, user_from, **kwargs):
        keywords = kwargs.pop('keywords')
        languages = kwargs.pop('languages', [])
        questions = kwargs.pop('questions', [])
        budgets = kwargs.pop('budgets', [])
        users_tagged = kwargs.pop('users_tagged', [])
        draft = kwargs.pop('draft', False)
        files = kwargs.pop('files', [])
        opportunity = self.create(
            created_by=user_from,
            **kwargs
        )
        self.update_budget(opportunity, budgets)
        self.update_files(opportunity, files)
        opportunity.save()
        opportunity.history.create(
            status=settings.OPPORTUNITIES_CH_DRAFT,
            user=user_from,
        )
        self._create_questions(opportunity, questions)
        self._create_users_tagged(opportunity, users_tagged)
        opportunity.keywords.add(*keywords)
        opportunity.languages.add(*languages)

        raise_exceptions = True
        if settings.POPULATOR_MODE:
            raise_exceptions = False
        if not draft:
            opportunity.send(
                user_from, raise_exceptions)
            opportunity.see(user_from, notify=False)
        return opportunity

    def update_opportunity(self, user_from, opportunity, **kwargs):
        if opportunity.group:
            kwargs.pop('entity', None)
            kwargs.pop('exo_role', None)
            kwargs.pop('budgets', None)
            kwargs.pop('duration_unity', None)
            kwargs.pop('duration_value', None)
        keywords = kwargs.pop('keywords')
        languages = kwargs.pop('languages', [])
        questions = kwargs.pop('questions', [])
        comment = kwargs.pop('comment', '')
        budgets = kwargs.pop('budgets', [])
        files = kwargs.pop('files', [])
        send_notification = kwargs.pop('send_notification', False)
        target_changed = (kwargs.pop('target'), opportunity.target)
        users_tagged_changed = (
            kwargs.pop('users_tagged', []),
            list(opportunity.users_tagged.values_list('user__uuid', flat=True))
        )
        for item, value in kwargs.items():
            setattr(opportunity, item, value)
        self.update_budget(opportunity, budgets)
        self.update_questions(opportunity, questions)
        self.update_files(opportunity, files)
        opportunity.clear_location()
        opportunity.save()
        opportunity.keywords.clear()
        opportunity.keywords.add(*keywords)
        opportunity.languages.clear()
        opportunity.languages.add(*languages)
        opportunity.refresh_from_db()
        opportunity_post_edited.send(
            sender=opportunity.__class__,
            opportunity=opportunity,
            comment=comment or '',
            send_notification=send_notification or False,
            target_change=target_changed,
            users_tagged_change=users_tagged_changed)
        return opportunity

    def all_my_opportunities(self, user=None):
        return self.get_queryset().filter_by_user(user).order_by_date()

    def filter_for_admin(self):
        return self.get_queryset().not_removed().not_draft().order_by_date()

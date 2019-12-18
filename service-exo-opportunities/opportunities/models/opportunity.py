import uuid

from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericRelation

from django_extensions.db.fields import AutoSlugField
from datetime import timedelta
from dateutil.relativedelta import relativedelta

from auth_uuid.utils.user_wrapper import UserWrapper
from model_utils.models import TimeStampedModel
from sortedm2m.fields import SortedManyToManyField

from utils.permissions import PermissionManagerMixin
from utils.models import CreatedByMixin
from utils.descriptors import ChoicesDescriptorMixin
from languages.models import Language

from ..conf import settings
from ..manager.opportunity import OpportunityManager
from .mixins import (
    OpportunityApplicantMixin,
    OpportunityUserStatusMixin,
    ActionStatsMixin,
    OpportunityConversationMixin,
    OpportunityActionsMixin,
    OpportunityTaggedMixin,
    OpportunityFileMixin,
)
from ..origin_helper import get_exo_project_info_by_uuid, get_event_info_by_uuid


class Opportunity(
        OpportunityApplicantMixin,
        OpportunityUserStatusMixin,
        OpportunityConversationMixin,
        OpportunityActionsMixin,
        OpportunityTaggedMixin,
        OpportunityFileMixin,
        ActionStatsMixin,
        PermissionManagerMixin,
        ChoicesDescriptorMixin,
        CreatedByMixin,
        TimeStampedModel):

    _status = models.CharField(
        max_length=1,
        choices=settings.OPPORTUNITIES_CH_STATUS,
        default=settings.OPPORTUNITIES_CH_STATUS_DEFAULT,
    )

    slug = AutoSlugField(
        populate_from='title',
        unique=True,
        null=True,
        blank=False,
    )
    target = models.CharField(
        max_length=1,
        choices=settings.OPPORTUNITIES_CH_TARGET,
        default=settings.OPPORTUNITIES_CH_TARGET_OPEN,
    )
    uuid = models.UUIDField(default=uuid.uuid4)
    title = models.CharField(max_length=200)
    description = models.TextField(
        'Details', blank=True, null=True)

    keywords = models.ManyToManyField('keywords.Keyword')

    mode = models.CharField(
        max_length=1,
        choices=settings.OPPORTUNITIES_CH_MODE_CHOICES,
        blank=True, null=True,
    )
    location = models.CharField(
        max_length=200,
        blank=True, null=True,
        default=None,
    )
    place_id = models.CharField(blank=True, null=True, max_length=255)
    location_url = models.URLField(blank=True, null=True)

    start_date = models.DateField(
        blank=True, null=True)
    deadline_date = models.DateField(
        blank=True, null=True)

    duration_unity = models.CharField(
        max_length=1,
        blank=True, null=True,
        choices=settings.OPPORTUNITIES_DURATION_UNITY_CHOICES,
    )
    duration_value = models.IntegerField(blank=True, null=True)

    exo_role = models.ForeignKey(
        'exo_role.ExORole',
        on_delete=models.SET_NULL,
        blank=True, null=True)
    certification_required = models.ForeignKey(
        'exo_role.CertificationRole',
        on_delete=models.SET_NULL,
        blank=True, null=True)
    other_role_name = models.CharField(
        max_length=200,
        blank=True, null=True,
    )
    files = GenericRelation('files.UploadedFile')
    other_category_name = models.CharField(
        max_length=200,
        blank=True, null=True,
    )

    entity = models.CharField(
        max_length=200,
        blank=True, null=True,
        default=None,
    )

    budget = models.CharField(
        max_length=200,
        blank=True, null=True,
        default=None)
    budget_currency = models.CharField(
        max_length=1,
        blank=True, null=True,
        default=settings.OPPORTUNITIES_CH_CURRENCY_DEFAULT,
        choices=settings.OPPORTUNITIES_CH_CURRENCY)

    virtual_budget = models.FloatField(
        default=0,
        blank=True, null=True,
    )
    virtual_budget_currency = models.CharField(
        max_length=1,
        blank=True, null=True,
        default=settings.OPPORTUNITIES_CH_VIRTUAL_CURRENCY_DEFAULT,
        choices=settings.OPPORTUNITIES_CH_VIRTUAL_CURRENCY,
    )
    applicants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='Applicant',
        related_name='opportunities',
    )
    sent_at = models.DateTimeField(
        blank=True, null=True)
    num_positions = models.IntegerField(
        default=1)
    group = models.ForeignKey(
        'OpportunityGroup',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='opportunities')
    languages = SortedManyToManyField(Language)

    context_object_uuid = models.UUIDField(
        blank=True, null=True)
    context_content_type = models.CharField(
        choices=settings.OPPORTUNITIES_CH_CONTEXT,
        max_length=20,
        blank=True, null=True)
    objects = OpportunityManager()

    CHOICES_DESCRIPTOR_FIELDS = ['_status', 'target', 'mode', 'duration_unity']

    class Meta:
        ordering = ['created']
        permissions = settings.OPPORTUNITIES_PERMS_ALL_PERMISSIONS
        verbose_name_plural = 'Opportunities'

    def __str__(self):
        return self.title

    @property
    def location_string(self):
        location_string = self.location
        if self.is_online:
            location_string = 'Online'
            if self.location_url:
                location_string += ' ({})'.format(self.location_url)

        return location_string or ''

    @property
    def role_string(self):
        OTHER_ROLES = [
            settings.EXO_ROLE_CODE_OTHER_OTHER,
            settings.EXO_ROLE_CODE_SPRINT_OTHER,
        ]
        if self.exo_role.code in OTHER_ROLES:
            return self.other_role_name
        else:
            return self.exo_role.name

    @property
    def budget_string(self):
        regular_budget_string = None
        cripto_budget_string = None
        if self.budget:
            regular_budget_string = '{} {}'.format(
                self.budget,
                self.get_budget_currency_display()
            )
        if self.virtual_budget:
            cripto_budget_string = '{} {}'.format(
                self.virtual_budget,
                self.get_virtual_budget_currency_display(),
            )
        if regular_budget_string is None and cripto_budget_string is None:
            return ''
        return '{} {}'.format(
            regular_budget_string if regular_budget_string is not None else cripto_budget_string,   # noqa
            'and ' + cripto_budget_string if regular_budget_string is not None and cripto_budget_string is not None else ''  # noqa
        )

    @property
    def budgets(self):
        budgets = []
        if self.budget:
            budgets.append({
                'budget': self.budget.__str__(),
                'currency': self.budget_currency
            })
        if self.virtual_budget:
            budgets.append({
                'budget': self.virtual_budget.__str__(),
                'currency': self.virtual_budget_currency
            })
        return budgets

    def set_target(self, new_target):
        self.target = new_target
        self.save(update_fields=['target', 'modified'])

    def _serialize_user_by(self, user_by, date):
        user_wrapper = UserWrapper(user=user_by)
        return {
            'created': date.isoformat(),
            'user': {
                'uuid': str(user_by.uuid),
                'email': user_wrapper.email,
                'fullName': user_wrapper.full_name,
                'user_title': user_wrapper.user_title,
            }
        }

    @property
    def url_public(self):
        return '{}{}'.format(
            settings.OPPORTUNITIES_PUBLIC_URL,
            self.id)

    @property
    def admin_url_public(self):
        if self.group:
            return '{}/{}'.format(
                self.group.advisor_request_section,
                self.id)
        else:
            return '{}{}'.format(
                settings.OPPORTUNITIES_ADMIN_URL,
                self.id)

    @property
    def date_sent(self):
        date_sent = None
        sent_action = self.history.filter(
            status=settings.OPPORTUNITIES_CH_REQUESTED).last()
        if sent_action:
            date_sent = sent_action.created

        return date_sent

    @property
    def end_date(self):
        end_date = None

        if self.is_hour or self.is_minute:
            end_date = self.start_date
        else:
            if self.is_day:
                delta = timedelta(days=self.duration_value)
            elif self.is_week:
                delta = timedelta(weeks=self.duration_value)
            elif self.is_month:
                delta = relativedelta(months=self.duration_value)

            end_date = self.start_date + delta

        return end_date

    @property
    def duration(self):
        if self.duration_value is None:
            return ''
        duration = '{} {}'.format(self.duration_value, self.get_duration_unity_display())

        if self.duration_value > 1:
            duration += 's'

        return duration

    @property
    def is_new(self):
        if not self.date_sent:
            return False
        days = (timezone.now() - self.date_sent).days
        return days < settings.OPPORTUNITIES_IS_NEW_TIMEDELTA_DAYS

    def clear_location(self):
        if self.is_onsite:
            self.location_url = None
        else:
            self.location = None
            self.place_id = None

    @property
    def has_been_edited(self):
        return self.created != self.modified

    @property
    def category(self):
        return self.exo_role.categories.first()

    @property
    def context_info_detail(self):
        if self.context_content_type == settings.OPPORTUNITIES_CH_CONTEXT_PROJECT:
            response = get_exo_project_info_by_uuid(self.context_object_uuid)
            return response.get('name')
        elif self.context_content_type == settings.OPPORTUNITIES_CH_CONTEXT_EVENT:
            response = get_event_info_by_uuid(self.context_object_uuid)
            return response.get('title')
        return None

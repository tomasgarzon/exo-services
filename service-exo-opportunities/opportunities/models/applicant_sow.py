from django.db import models
from django.contrib.postgres.fields import JSONField
from django.urls import reverse

from model_utils.models import TimeStampedModel
from utils.descriptors import ChoicesDescriptorMixin
from utils.mixins import TimezoneMixin

from ..conf import settings


class ApplicantSow(
    ChoicesDescriptorMixin,
    TimezoneMixin,
    TimeStampedModel,
):

    applicant = models.OneToOneField(
        'Applicant',
        blank=True, null=True,
        on_delete=models.CASCADE,
        related_name='sow')
    title = models.CharField(max_length=200)
    requester_name = models.CharField(
        max_length=200, null=True, blank=False)
    applicant_name = models.CharField(
        max_length=200, null=True, blank=False)
    description = models.TextField(
        'Details', blank=True, null=True)

    mode = models.CharField(
        max_length=1,
        choices=settings.OPPORTUNITIES_CH_MODE_CHOICES,
        default=settings.OPPORTUNITIES_CH_MODE_DEFAULT,
    )
    location = models.CharField(
        max_length=200,
        blank=True, null=True,
        default=None,
    )
    place_id = models.CharField(blank=True, null=True, max_length=255)
    location_url = models.URLField(blank=True, null=True)

    start_date = models.DateField(
        blank=False, null=True)
    start_time = models.TimeField(
        blank=True, null=True)
    end_date = models.DateField(
        blank=False, null=True)
    duration_unity = models.CharField(
        max_length=1,
        blank=True, null=True,
        choices=settings.OPPORTUNITIES_DURATION_UNITY_CHOICES,
    )
    duration_value = models.IntegerField(blank=True, null=True)
    entity = models.CharField(
        max_length=200,
        blank=True, null=True,
        default=None,
    )
    budgets = JSONField(blank=True, null=True)
    reimbursable_expenses = models.BooleanField(
        blank=True, default=False)
    extra_expenses = models.TextField(blank=True, null=True)

    CHOICES_DESCRIPTOR_FIELDS = ['mode']

    class Meta:
        ordering = ['created']

    def __str__(self):
        return self.title

    def update_sow(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.save()

    @property
    def download_url(self):
        return reverse('opportunities:download-sow-pdf', kwargs={'pk': self.applicant.pk})

    @property
    def budget_string(self):
        regular_budget_string = None
        cripto_budget_string = None
        budget = list(filter(
            lambda x: x['currency'] in dict(settings.OPPORTUNITIES_CH_CURRENCY).keys(),
            self.budgets))
        virtual_budget = list(filter(
            lambda x: x['currency'] in dict(settings.OPPORTUNITIES_CH_VIRTUAL_CURRENCY).keys(),
            self.budgets))
        if len(budget) > 0:
            budget = budget[0]
            regular_budget_string = '{} {}'.format(
                budget['budget'],
                dict(settings.OPPORTUNITIES_CH_CURRENCY).get(budget['currency'])
            )
        if len(virtual_budget) > 0:
            virtual_budget = virtual_budget[0]
            cripto_budget_string = '{} {}'.format(
                virtual_budget['budget'],
                dict(settings.OPPORTUNITIES_CH_VIRTUAL_CURRENCY).get(virtual_budget['currency']),
            )

        return '{} {}'.format(
            regular_budget_string if regular_budget_string is not None else cripto_budget_string,   # noqa
            'and ' + cripto_budget_string if regular_budget_string is not None and cripto_budget_string is not None else ''  # noqa
        )

    @property
    def location_string(self):
        location_string = self.location

        if self.is_online:
            location_string = 'Online'

            if self.location_url:
                location_string += ' ({})'.format(self.location_url)

        return location_string

    @property
    def date_sow_accepted(self):
        history = self.applicant.history.filter(
            status=settings.OPPORTUNITIES_CH_APPLICANT_SOW_ACCEPTED).first()
        return history.created

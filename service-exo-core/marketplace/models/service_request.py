from django.db import models

from model_utils.models import TimeStampedModel

from utils.mail import handlers
from utils.mail.mails_mixin import EmailMixin
from utils.models import CreatedByMixin

from ..conf import settings


class ServiceRequest(EmailMixin, CreatedByMixin, TimeStampedModel):
    name = models.CharField(max_length=254)
    last_name = models.CharField(max_length=254)
    email = models.EmailField()
    company = models.CharField(max_length=254, blank=True, null=True)
    position = models.CharField(max_length=254, blank=True, null=True)
    country = models.CharField(max_length=254)
    status = models.CharField(
        max_length=1,
        choices=settings.MARKETPLACE_CH_STATUS,
        default=settings.MARKETPLACE_CH_STATUS_DEFAULT,
    )
    participant = models.CharField(
        max_length=1,
        choices=settings.MARKETPLACE_CH_PARTICIPANT,
        default=settings.MARKETPLACE_CH_PARTICIPANT_DEFAULT,
    )
    motivation = models.CharField(
        max_length=1,
        choices=settings.MARKETPLACE_CH_MOTIVATION,
        default=settings.MARKETPLACE_CH_MOTIVATION_DEFAULT,
    )
    motivation_other = models.TextField(blank=True, null=True)
    goal = models.CharField(
        max_length=1,
        choices=settings.MARKETPLACE_CH_GOAL,
        default=settings.MARKETPLACE_CH_GOAL_DEFAULT,
    )
    employees = models.CharField(
        max_length=1,
        choices=settings.MARKETPLACE_CH_EMPLOYEES_RANGE,
        default=settings.MARKETPLACE_CH_EMPLOYEES_RANGE_DEFAULT,
        blank=True, null=True
    )
    initiatives = models.CharField(
        max_length=1,
        choices=settings.MARKETPLACE_CH_INITIATIVES_RANGE,
        default=settings.MARKETPLACE_CH_INITIATIVES_RANGE_DEFAULT,
        blank=True, null=True
    )
    book = models.BooleanField(default=False)
    comment = models.TextField()

    class Meta:
        verbose_name_plural = 'Service Request'
        verbose_name = 'Service Requests'

    def __str__(self):
        return self.email

    def notify_managers_email(self):

        recipients = self.get_group_destinataries(settings.MARKETPLACE_GROUP_NAME)

        mail_kwargs = {
            'name': self.name,
            'email': self.email,
            'company': self.company,
            'position': self.position,
            'participant': self.get_participant_display(),
            'motivation': self.get_motivation_display(),
            'employees': self.get_employees_display(),
            'initiatives': self.get_initiatives_display(),
            'goal': self.get_goal_display(),
            'book': self.book,
            'comment': self.comment,
        }
        handlers.mail_handler.send_mail(
            'marketplace_service_request',
            recipients=recipients,
            **mail_kwargs)

from django.db import models
from django.templatetags.static import static
from django.conf import settings

from model_utils.models import TimeStampedModel
from versionfield import VersionField

from utils.descriptors import ChoicesDescriptorMixin
from django.template.loader import render_to_string

from ..managers.agreement import AgreementManager


class Agreement(ChoicesDescriptorMixin, TimeStampedModel):

    name = models.CharField(
        verbose_name='Name',
        max_length=100,
    )
    description = models.CharField(
        verbose_name='Agreement description',
        max_length=100,
        blank=True, null=True,
    )
    file_name = models.CharField(
        verbose_name='Agreement file name',
        max_length=200,
    )

    document_name = models.CharField(
        default=settings.BRAND_NAME + ' Agreement v',
        verbose_name='Agreement document name',
        max_length=200,
    )

    version = VersionField()

    recipient = models.CharField(
        max_length=1,
        default=settings.AGREEMENT_RECIPIENT_DEFAULT,
        choices=settings.AGREEMENT_RECIPIENT,
        blank=False, null=False,
    )

    status = models.CharField(
        max_length=1,
        default=settings.AGREEMENT_STATUS_DEFAULT,
        choices=settings.AGREEMENT_STATUS,
        blank=False, null=False,
    )
    domain = models.CharField(
        max_length=1,
        default=settings.AGREEMENT_DOMAIN_DEFAULT,
        choices=settings.AGREEMENT_DOMAIN_CHOICES,
    )

    CHOICES_DESCRIPTOR_FIELDS = ['status', 'domain']

    objects = AgreementManager()

    def __str__(self):
        return '{} for {} - {}'.format(
            self.name,
            self.get_recipient_display(),
            self.get_status_display(),
        )

    @property
    def date_cancelled(self):
        return self.modified if self.is_cancelled else None

    @property
    def date_activation(self):
        return self.modified if self.is_active else None

    @property
    def html(self):
        return render_to_string(self.template_name)

    @property
    def template_name(self):
        return '{}/{}'.format(
            settings.AGREEMENT_TEMPLATE_FOLDER,
            self.file_name,
        )

    @property
    def file_url(self):
        version = str(self.version).split('.')[0]
        return static(
            '{}/{}{}.pdf'.format(
                settings.AGREEMENT_TEMPLATE_FOLDER,
                self.document_name,
                version,
            ),
        )

    def set_status(self, status):
        self.status = status
        self.save(update_fields=['status', 'modified'])

    def cancel_old_agreements(self):
        Agreement.objects.filter_by_status_active().filter(
            recipient=self.recipient,
        ).update(status=settings.AGREEMENT_STATUS_CANCELLED)

    def activate(self):
        self.cancel_old_agreements()
        self.set_status(settings.AGREEMENT_STATUS_ACTIVE)

import logging
from io import BytesIO

from django.core.exceptions import ValidationError
from django.db import models
from django.template.defaultfilters import truncatechars
from django.urls import reverse
from django.core.files import File

from model_utils.models import TimeStampedModel
from forex_python.converter import CurrencyRates
from wkhtmltopdf.utils import render_pdf_from_template

from utils.models import CreatedByMixin, EmailMixin
from utils.descriptors import ChoicesDescriptorMixin
from utils.crypto import AESCipher

from .stripe_intent_mixin import StripeIntentMixin
from .stripe_charge_mixin import StripeChargeMixin
from .invoice_serie import InvoiceSerie
from .. import tasks
from ..conf import settings
from ..signals_define import payment_status_changed


SEPARATOR = '__'

logger = logging.getLogger('service')


def directory_path(instance, filename):
    return 'temp_attached/{}{}{}'.format(
        instance._hash_code,
        SEPARATOR,
        filename,
    )


def validate_pdf_file(value):
    if not value.name.endswith('.pdf'):
        raise ValidationError(
            'File format not supported, please attach PDF files.'
        )


class Payment(
        StripeIntentMixin,
        StripeChargeMixin,
        EmailMixin,
        ChoicesDescriptorMixin,
        CreatedByMixin,
        TimeStampedModel):

    uuid = models.UUIDField(
        editable=False,
        null=True)
    _hash_code = models.CharField(max_length=256, blank=True, null=True)
    _stripe_payment_id = models.CharField(
        max_length=256,
        blank=True,
        null=True,
    )
    _type = models.CharField(
        max_length=1,
        blank=True,
        null=True,
        choices=settings.PAYMENTS_TYPE_CHOICES,
    )

    invoice_id = models.CharField(max_length=64, blank=True, null=True)

    amount = models.DecimalField(max_digits=20, decimal_places=2)
    currency = models.CharField(
        max_length=4,
        choices=settings.PAYMENTS_PAYMENT_CURRENCY,
        default=settings.PAYMENTS_CH_EUR,
    )
    notes = models.TextField(blank=True, null=True)

    concept = models.CharField(max_length=512)
    detail = models.TextField(blank=True, null=True)

    email = models.EmailField()
    full_name = models.CharField(max_length=200)
    company_name = models.CharField(max_length=200, blank=True, null=True)
    country = models.CharField(max_length=200, blank=True, null=True)
    country_code = models.CharField(max_length=3, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    tax_id = models.CharField(max_length=200, blank=True, null=True)

    attached_file = models.FileField(
        upload_to=directory_path,
        validators=[validate_pdf_file],
        blank=True,
        null=True,
    )

    status = models.CharField(
        max_length=1,
        choices=settings.PAYMENTS_PAYMENT_STATUS,
        default=settings.PAYMENTS_CH_PENDING,
    )

    alternative_payment_mode = models.CharField(
        max_length=1,
        blank=True,
        null=True,
        choices=settings.PAYMENTS_ALTERNATIVE_PAYMENT,
    )
    alternative_payment_comment = models.TextField(blank=True, null=True)
    send_by_email = models.BooleanField(default=True)
    send_invoice = models.BooleanField(default=False)
    date_payment = models.DateTimeField(blank=True, null=True)
    url_notification = models.URLField(blank=True, null=True)
    rate = models.FloatField(blank=True, null=True)
    vat = models.IntegerField(
        blank=False,
        null=True,
        default=0,
    )

    CHOICES_DESCRIPTOR_FIELDS = ['status', 'currency']

    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'

    def __str__(self):
        return '{} - {}'.format(self.concept, self.full_name)

    def set_invoice_id(self):
        if not self.invoice_id:
            serie = '{}{}'.format(self._type, self.created.year.__str__()[2:])
            self.invoice_id = InvoiceSerie.create(serie)
            self.save(update_fields=['invoice_id'])

    @property
    def concept_excerpt(self):
        return truncatechars(self.concept, 100)

    @property
    def url(self):
        return reverse(
            'payments:do_payment', kwargs={'slug': self._hash_code})

    @property
    def absolute_url(self):
        return '{}/{}'.format(
            settings.DOMAIN_NAME,
            self.url[1:],
        )

    @property
    def amount_normalized(self):
        return int('{}'.format(self.amount).replace('.', ''))

    @property
    def payment_code(self):
        return self._hash_code

    @property
    def amount_str(self):
        return '{} {}'.format(
            '$' if self.is_usd else self.amount,
            self.amount if self.is_usd else '€',
        )

    @property
    def attached_filename(self):
        attached_filename = None
        if self.attached_file.name:
            attached_filename = self.attached_file.name.split('/')[-1].split(SEPARATOR)[-1]

        return attached_filename

    @property
    def token(self):
        response = {}
        response['concept'] = self.concept
        response['amount'] = self.amount
        response['currency'] = self.currency
        response['email'] = self.email
        response['uuid'] = self.uuid
        cipher = AESCipher()
        return cipher.encrypt(str(response))

    def notify_webhook(self):
        if self.url_notification:
            logger.info(
                'Payment.notify_webhook(): Payment {} (pk: {}) send notification.'.format(self, self.pk))
            tasks.SendWebhookTask().s(pk=self.pk).apply_async()
        else:
            logger.info(
                'Payment.notify_webhook(): Payment {} (pk: {}) has no url to notify.'.format(self, self.pk))

    @property
    def final_rate(self):
        c = CurrencyRates()
        if self.is_eur:
            return 1
        else:
            self.rate = c.get_rate(
                self.currency.upper(),
                settings.PAYMENTS_CH_EUR.upper())
            return self.rate * 0.99

    @property
    def amount_eur(self):
        if self.is_usd:
            res = float(self.amount) * self.final_rate
        else:
            res = float(self.amount)
        return round(res, 2)

    @property
    def has_VAT(self):
        return self.country_code == settings.PAYMENTS_COUNTRY_SPAIN

    @property
    def amount_vat(self):
        res = 0
        if self.vat:
            res = self.vat * 0.01 * self.amount_eur
        return round(res, 2)

    @property
    def amount_total(self):
        if self.has_VAT:
            res = self.amount_eur + self.amount_vat
        else:
            res = self.amount_eur
        return round(res, 2)

    def calculate_amount(self, force_no_rate=False):
        if force_no_rate:
            self.rate = None
        if self.rate is not None:
            return
        if self.has_VAT:
            self.vat = settings.PAYMENTS_VAT_DEFAULT
        self.save()

    def generate_invoice(self):
        self.set_invoice_id()
        response = render_pdf_from_template(
            'invoices/invoice.html', None, None,
            context={'object': self})
        self.attached_file.save(
            'invoice{}.pdf'.format(self.invoice_id),
            File(BytesIO(response)))

    @property
    def is_european(self):
        code = self.country_code
        return code in settings.PAYMENTS_INVOICE_COUNTRY_RELATION.get(
            settings.PAYMENTS_EUROPE_INVOICE)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        original = type(self).objects.get(pk=self.pk) if self.pk else None
        super().save(*args, **kwargs)
        if is_new or original and original.status != self.status:
            payment_status_changed.send(sender=self.__class__, payment=self)

from django.contrib import admin
from django.conf import settings
from import_export import resources
from import_export.admin import ExportMixin

from . import models


class PaymentResource(resources.ModelResource):

    class Meta:
        fields = (
            'amount',
            'currency',
            'concept',
            'full_name',
            'email',
            'status',
            'rate',
            'date_payment',
        )
        model = models.Payment

    def dehydrate_status(self, instance):
        return instance.get_status_display()


class PaymentsAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = PaymentResource
    fieldsets = (
        ('User data', {
            'fields': (
                ('full_name', 'email',),
                ('company_name', 'country', 'country_code'),
                ('address', 'tax_id')),
        }),
        ('Payment information', {
            'fields': (
                'invoice_id',
                'concept',
                'detail',
                '_type',
                ('amount', 'currency'),
                ('rate', 'vat'),
                'attached_file',
                'url_notification',
                ('email_status', 'email_link_tag',),
            ),
        }),
        ('Payment details', {
            'fields': (
                ('status', 'date_payment'),
                ('alternative_payment_mode', 'alternative_payment_comment'),
            ),
        }),
        ('Stipe data', {
            'fields': (
                'intent_id',
                '_hash_code',
                '_stripe_auth_token_code',
                '_stripe_payment_id',
            )
        })
    )

    readonly_fields = (
        'intent_id',
        '_hash_code',
        '_stripe_auth_token_code',
        '_stripe_payment_id',
        'date_payment',
        'url_notification',
        'email_status',
        'uuid',
        'email_link_tag',
        'rate',
        'amount_str',
        'amount_total',
    )
    search_fields = ('email', 'full_name', 'invoice_id', )
    list_filter = ('status', )
    list_display = (
        'user',
        'invoice_id',
        'concept_excerpt',
        'payment_amount',
        'amount_eur',
        'vat_percent',
        'final_amount',
        'payment_url',
        'uuid',
        'created',
        'paid_at',
        'status',
    )

    def user(self, obj):
        return '{} - {}'.format(obj.full_name, obj.email)

    def vat_percent(self, obj):
        percent = obj.vat if obj.vat else 0
        return '{} %'.format(percent)

    def final_amount(self, obj):
        return '{} €'.format(obj.amount_total)

    def payment_amount(self, obj):
        return obj.amount_str

    def paid_at(self, obj):
        paid_at = '-'
        if obj.is_paid:
            paid_at = obj.date_payment

        return paid_at

    def payment_url(self, obj):
        return '{}{}'.format(
            settings.DOMAIN_NAME,
            obj.url
        )


admin.site.register(models.Payment, PaymentsAdmin)
admin.site.register(models.InvoiceSerie)

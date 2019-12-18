from django.contrib import admin

from . import models


@admin.register(models.CertificationRequest)
class CertificationRequestAdmin(admin.ModelAdmin):
    search_fields = (
        'user__email',
        'user__full_name',
        'requester_name',
        'requester_email',
        'certification__level',
        'hubspot_deal',
    )
    list_filter = ('status', 'cohort', 'certification',)
    list_display = (
        'user_info',
        'status',
        'coupon',
        'level',
        'cohort',
        'created',
        'payment_uuid',
        'price',
        'hubspot_deal',
    )

    def user_info(self, instance):
        if instance.user:
            return '{} <{}>'.format(instance.user.full_name, instance.user.email)
        else:
            return '{} <{}>'.format(instance.requester_name, instance.requester_email)

    def cohort(self, instance):
        if instance.cohort:
            cohort = ' [{}] {}'.format(
                instance.cohort.language,
                instance.cohort.date,
            )
        else:
            cohort = ''
        return '{}{}'.format(
            instance.certification.level,
            cohort,
        )

    readonly_fields = (
        'payment_url',
        'created',
        'payment_uuid',
        'application_details',
        'referrer',
    )


@admin.register(models.Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'level', 'discount', 'type', 'owner', 'expiry_date', 'max_uses', 'uses')


@admin.register(models.CertificationCohort)
class CertificationCohortAdmin(admin.ModelAdmin):
    list_filter = ('language', 'currency', 'status')
    list_display = ('title', 'level', 'date', 'language', 'seats', 'price', 'first_price_tier')


@admin.register(models.ExOCertification)
class ExOCertificationAdmin(admin.ModelAdmin):
    list_display = ('name', 'level', 'certification_role', 'description',)

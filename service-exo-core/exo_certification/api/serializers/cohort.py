from django.conf import settings

from rest_framework import serializers

from exo_certification.models import Coupon
from ...helpers.payment import final_price_coupon
from ...models import CertificationCohort


class CohortSerializer(serializers.ModelSerializer):
    discount = serializers.SerializerMethodField()
    final_price = serializers.SerializerMethodField()
    referral_code = serializers.SerializerMethodField()

    class Meta:
        model = CertificationCohort
        fields = [
            'currency',
            'date',
            'discount',
            'final_price',
            'pk',
            'price',
            'title',
            'referral_code',
        ]

    def get_referral_code(self, instance):
        if self.get_discount(instance):
            return self.context['request'].GET.get('coupon')
        return None

    def get_discount(self, instance):
        code = self.context['request'].GET.get('coupon', None)
        discount = None
        try:
            coupon = Coupon.objects.get(code=code)
            if coupon.certification == instance.certification:
                if coupon.type == settings.EXO_CERTIFICATION_COUPON_TYPES_CH_AMOUNT:
                    discount = coupon.discount
                else:
                    discount = instance.price * coupon.discount * 0.01
        except Coupon.DoesNotExist:
            pass
        return discount

    def get_final_price(self, instance):
        return final_price_coupon(
            code=self.context['request'].GET.get('coupon', None),
            cohort=instance,
        )

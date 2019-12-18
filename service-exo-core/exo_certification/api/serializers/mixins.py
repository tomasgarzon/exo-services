import itertools

from django.conf import settings

from rest_framework import serializers

from ...models import Coupon


class CertificationLevelMixin(serializers.Serializer):
    level = serializers.CharField()

    def validate_level(self, value):
        if value not in itertools.chain(*settings.EXO_CERTIFICATION_LEVEL_CH_LEVELS):
            raise serializers.ValidationError('Level is not valid')
        return value


class CouponMixin(serializers.Serializer):
    coupon = serializers.CharField(required=False, allow_blank=True)

    def validate_coupon(self, value):
        if not value:
            return None
        try:
            coupon = Coupon.objects.get(code=value)
        except Coupon.DoesNotExist:
            raise serializers.ValidationError('Coupon does not exist')

        if not coupon.is_available:
            raise serializers.ValidationError('Coupon expired')

        if self.instance and not coupon.check_for_user(self.instance.user):
            raise serializers.ValidationError('Coupon does not exist')

        return coupon

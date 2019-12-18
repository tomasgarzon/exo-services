from django.conf import settings
from django.core.exceptions import ValidationError

from rest_framework import serializers

from utils.crypto.crypto import AESCipher
from utils.segment import SegmentAnalytics


class PaymentsWebhookSerializer(serializers.Serializer):
    token = serializers.CharField()
    payment_id = serializers.CharField()
    payment_status = serializers.CharField()
    payment_method = serializers.CharField()

    def validate_token(self, value):
        try:
            cipher = AESCipher(settings.PAYMENT_SECRET_KEY)
            assert cipher.decrypt(value)
        except AssertionError:
            raise ValidationError('Token not valid')

        return value

    def to_representation(self, obj):
        return {
            'payment_uuid': obj.payment_uuid,
            'status': obj.status,
        }

    def update(self, instance, validated_data):
        payment_status = validated_data.get('payment_status')

        instance.validate_payment(payment_status)
        instance.refresh_from_db()

        if payment_status == settings.EXO_CERTIFICATION_REQUEST_STATUS_CH_APPROVED:
            category = settings.EXO_CERTIFICATION_INSTRUMENTATION_EVENTS.get(
                instance.level)
            SegmentAnalytics.event(
                user=instance.user,
                category=category,
                event=settings.INSTRUMENTATION_EVENT_CERTIFICATION_UPDATED,
                action_done=settings.INSTRUMENTATION_CERTIFICATION_ACTION_PAY,
                cohort=instance.cohort.date,
                language=instance.cohort.language,
                final_price=instance.price,
                payment_method=validated_data.get('payment_method')
            )

        return instance

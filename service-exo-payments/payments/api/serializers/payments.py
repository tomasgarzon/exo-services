from django.conf import settings

from rest_framework import serializers, exceptions

from ...models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    payment_uuid = serializers.CharField(source='uuid')
    next_url = serializers.CharField(source='absolute_url')

    class Meta:
        model = Payment
        fields = [
            'payment_uuid',
            'next_url',
        ]


class CreatePaymentSerializer(serializers.ModelSerializer):
    type_payment = serializers.CharField(source='_type')
    notify_webhook = serializers.CharField(source='url_notification', required=False)

    class Meta:
        model = Payment
        fields = [
            'amount', 'currency',
            'concept', 'detail',
            'email', 'full_name', 'tax_id',
            'address', 'country', 'country_code',
            'company_name',
            'type_payment', 'notes',
            'notify_webhook',
            'send_by_email'
        ]

    def create(self, validated_data):
        payment = Payment.objects.create(
            _type=validated_data.get('_type'),
            amount=validated_data.get('amount'),
            currency=validated_data.get('currency'),
            concept=validated_data.get('concept'),
            detail=validated_data.get('detail'),
            notes=validated_data.get('notes'),
            email=validated_data.get('email'),
            full_name=validated_data.get('full_name'),
            tax_id=validated_data.get('tax_id'),
            address=validated_data.get('address'),
            country=validated_data.get('country'),
            country_code=validated_data.get('country_code'),
            url_notification=validated_data.get('url_notification'),
            send_by_email=validated_data.get('send_by_email', False),
            send_invoice=True,
            status=settings.PAYMENTS_CH_PENDING,
        )

        payment.calculate_amount()
        return payment

    def to_representation(self, instance):
        return PaymentSerializer(instance).data


class UpdatePaymentSerializer(serializers.ModelSerializer):
    notify_webhook = serializers.CharField(source='url_notification', required=False)

    class Meta:
        model = Payment
        fields = [
            'amount',
            'currency',
            'concept',
            'detail',
            'email',
            'full_name',
            'tax_id',
            'address',
            'country',
            'country_code',
            'company_name',
            '_type',
            'notes',
            'notify_webhook',
            'send_by_email',
        ]

    def update(self, instance, validated_data):
        if instance.status not in settings.PAYMENTS_VALID_STATUS_UPDATE:
            return exceptions.NotFound

        instance = super().update(instance, validated_data)
        instance.calculate_amount(force_no_rate=True)
        return instance

    def to_representation(self, instance):
        return PaymentSerializer(instance).data

import hmac
import hashlib
import base64

from django.conf import settings

from rest_framework import serializers

from ...models import Payment


class DoRequestSerializer(serializers.ModelSerializer):
    token = serializers.CharField(required=True)
    url = serializers.URLField(required=True)

    class Meta:
        model = Payment
        fields = [
            'concept', 'amount', 'currency',
            'email', 'full_name',
            'token', 'url']

    def validate(self, data):
        response = {}
        response['concept'] = data.get('concept')
        response['amount'] = data.get('amount')
        response['currency'] = data.get('currency')
        response['email'] = data.get('email')
        response['full_name'] = data.get('full_name')
        token = data.get('token')
        secret_key = settings.PAYMENT_SECRET_KEY
        dig = hmac.new(
            secret_key.encode(),
            msg=str(response).encode(),
            digestmod=hashlib.sha256).digest()
        response_code = base64.b64encode(dig).decode()
        if token != response_code:
            raise serializers.ValidationError('Invalid Token')
        return data

    def create(self, validated_data):
        payment = Payment.objects.create(
            concept=validated_data.get('concept'),
            amount=validated_data.get('amount'),
            currency=validated_data.get('currency'),
            email=validated_data.get('email'),
            full_name=validated_data.get('full_name'),
            created_by=validated_data.get('created_by'),
        )

        if validated_data.get('url'):
            payment.url_notification = validated_data.get('url')
            payment.save()
        return payment

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import NotAuthenticated

from core.models import Country
from exo_certification.models import ExOCertification
from utils.drf.mixins.recaptcha_serializer import RecaptchaSerializerMixin
from utils.segment import SegmentAnalytics

from ...models import CertificationRequest, CertificationCohort
from .mixins import CertificationLevelMixin, CouponMixin
from ...helpers.payment import (
    user_can_do_certification,
    update_certification_request,
)


UserModel = get_user_model()


class CertificationOutputSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='requester_name')
    email = serializers.EmailField(source='requester_email')
    level = serializers.CharField(source='certification.level')

    class Meta:
        model = CertificationRequest
        fields = [
            'pk',
            'full_name',
            'email',
            'level',
        ]


class DraftCertificationSerializer(
        RecaptchaSerializerMixin,
        CertificationLevelMixin,
        CouponMixin,
        serializers.Serializer):

    full_name = serializers.CharField()
    email = serializers.EmailField(allow_blank=False)
    recaptcha = serializers.CharField(read_only=True)
    referrer = serializers.RegexField(
        '[a-zA-Z0-9]+:[a-zA-Z0-9]+', required=False, allow_blank=True)

    def validate_email(self, value):
        return UserModel._default_manager.normalize_email(value)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        coupon = attrs.get('coupon', None)
        certification = ExOCertification.objects.get(level=attrs['level'])
        if coupon and not coupon.can_use_coupon(certification, False):
            raise serializers.ValidationError({'coupon': ['Coupon is not valid']})
        return attrs

    def create(self, validated_data):
        email = validated_data.get('email')
        full_name = validated_data.get('full_name')
        level = validated_data.get('level')
        coupon = validated_data.get('coupon', None)
        referrer = validated_data.get('referrer', None)
        user = None

        try:
            user = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            pass

        if level == settings.EXO_CERTIFICATION_CERTIFICATION_CH_LEVEL_3:
            raise NotAuthenticated({'custom': 'LOGIN_REQUIRED_TO_PROCEED'})

        # Checks whether user can certificate or not
        requester = user if user else email
        certification = user_can_do_certification(requester, level)

        certification_request_defaults = {
            'requester_name': full_name,
        }

        certification_request, created = CertificationRequest.objects.get_or_create(
            certification=certification,
            requester_email=email,
            status__in=[
                settings.EXO_CERTIFICATION_REQUEST_STATUS_CH_DRAFT,
                settings.EXO_CERTIFICATION_REQUEST_STATUS_CH_PENDING,
            ],
            defaults=certification_request_defaults,
        )

        if created:
            certification_request.referrer = referrer

        if user:
            certification_request.user = user
            category = settings.EXO_CERTIFICATION_INSTRUMENTATION_EVENTS.get(
                certification_request.level)
            coupon_code = coupon.code if coupon else None
            SegmentAnalytics.event(
                user=user,
                category=category,
                event=settings.INSTRUMENTATION_EVENT_CERTIFICATION_INTERESTED,
                coupon=coupon_code,
                entry_point=settings.INSTRUMENTATION_USER_ENTRY_POINT_CERTIFICATIONS
            )

        certification_request.coupon = coupon
        certification_request.save(update_fields=['user', 'coupon', 'referrer'])

        return certification_request

    def to_representation(self, instance):
        return CertificationOutputSerializer(instance).data


class PendingCertificationSerializer(
        RecaptchaSerializerMixin,
        serializers.Serializer):
    cohort = serializers.PrimaryKeyRelatedField(queryset=CertificationCohort.objects.all())
    billing_name = serializers.CharField()
    tax_id = serializers.CharField(
        required=False, allow_blank=True)
    billing_address = serializers.CharField()
    country = serializers.SlugRelatedField(queryset=Country.objects.all(), slug_field='code_2')
    recaptcha = serializers.CharField(read_only=True)
    application_details = serializers.JSONField(required=False)

    def update(self, instance, validated_data):
        certification_request = update_certification_request(instance, validated_data)
        return certification_request

    def to_representation(self, instance):
        return {'next_url': instance.payment_url}

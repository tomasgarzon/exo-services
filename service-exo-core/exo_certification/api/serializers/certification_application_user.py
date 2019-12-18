from django.conf import settings
from django.contrib.auth import get_user_model

from rest_framework import serializers

from consultant.models import ContractingData, ConsultantExOProfile
from custom_auth.api.serializers.auth import LoginSerializer
from exo_certification.models import ExOCertification
from utils.drf.mixins.recaptcha_serializer import RecaptchaSerializerMixin
from utils.segment import SegmentAnalytics

from ...helpers.payment import user_can_do_certification
from ...models import CertificationRequest
from .certification_application import CertificationOutputSerializer
from .mixins import CertificationLevelMixin, CouponMixin

UserModel = get_user_model()


class ContractingDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractingData
        fields = [
            'name',
            'tax_id',
            'address',
            'company_name',
        ]


class CertificationUserOutput(CertificationOutputSerializer):
    contracting_data = serializers.SerializerMethodField()

    class Meta:
        model = CertificationRequest
        fields = [
            'pk',
            'email',
            'full_name',
            'level',
            'contracting_data',
        ]

    def get_contracting_data(self, instance):
        try:
            contracting_data = instance.user.consultant.exo_profile.contracting_data
        except (
            AttributeError,
            ConsultantExOProfile.DoesNotExist,
            ContractingData.DoesNotExist,
            Exception,
        ):
            contracting_data = None
        return ContractingDataSerializer(contracting_data).data


class DraftCertificationUserSerializer(
        RecaptchaSerializerMixin,
        LoginSerializer,
        CertificationLevelMixin,
        CouponMixin,
        serializers.Serializer):

    recaptcha = serializers.CharField(read_only=True)
    email = serializers.EmailField()
    username = serializers.EmailField(read_only=True)
    referrer = serializers.RegexField(
        '[a-zA-Z0-9]+:[a-zA-Z0-9]+', required=False, allow_blank=True)

    def validate(self, attrs):
        email = attrs.pop('email')
        attrs['username'] = email
        attrs = super().validate(attrs)
        coupon = attrs.get('coupon', None)
        certification = ExOCertification.objects.get(level=attrs['level'])
        if coupon and not coupon.can_use_coupon(certification, False):
            raise serializers.ValidationError({'coupon': ['Coupon is not valid']})
        return attrs

    def create(self, validated_data):
        level = validated_data.get('level')
        coupon = validated_data.get('coupon', None)
        referrer = validated_data.get('referrer', None)
        user = validated_data.get('user')

        certification = user_can_do_certification(user, level)

        certification_defaults = {
            'requester_name': user.full_name,
            'user': user,
        }

        certification_request, created = CertificationRequest.objects.get_or_create(
            certification=certification,
            requester_email=user.email,
            status__in=[
                settings.EXO_CERTIFICATION_REQUEST_STATUS_CH_DRAFT,
                settings.EXO_CERTIFICATION_REQUEST_STATUS_CH_PENDING,
            ],
            defaults=certification_defaults,
        )

        if created:
            certification_request.referrer = referrer

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
        certification_request.save()

        return certification_request

    def to_representation(self, instance):
        return CertificationUserOutput(instance).data

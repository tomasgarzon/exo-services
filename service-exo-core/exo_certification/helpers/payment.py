import logging
import requests

from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.exceptions import PermissionDenied

from consultant.models import Consultant
from exo_accounts.models import EmailAddress
from exo_certification.models import ExOCertification, CertificationRequest
from utils.segment import SegmentAnalytics

from .hubspot import get_entry_point_by_level
from ..models import Coupon


logger = logging.getLogger('service')


def get_root_payments_url():
    return '{}{}'.format(
        settings.EXOLEVER_HOST,
        settings.SERVICE_EXO_PAYMENT_HOST)


def final_price_coupon(code, cohort):
    price = cohort.price
    try:
        coupon = Coupon.objects.get(code=code)
        if coupon.is_available and coupon.certification == cohort.certification:
            if coupon.type == settings.EXO_CERTIFICATION_COUPON_TYPES_CH_PERCENT:
                price = price - price * coupon.discount * 0.01
            else:
                price = cohort.price - coupon.discount
    except Coupon.DoesNotExist:
        pass
    return price


def user_can_do_certification(user, level):
    try:
        certification = ExOCertification.objects.get(level=level)
        qs = CertificationRequest.objects.filter(
            certification=certification,
        ).exclude(status__in=[
            settings.EXO_CERTIFICATION_REQUEST_STATUS_CH_DRAFT,
            settings.EXO_CERTIFICATION_REQUEST_STATUS_CH_PENDING,
            settings.EXO_CERTIFICATION_REQUEST_STATUS_CH_CANCELLED,
        ])
        if isinstance(user, get_user_model()):
            qs = qs.filter(user=user)
        else:
            try:
                email = EmailAddress.objects.get(
                    email=get_user_model()._default_manager.normalize_email(user),
                )
                qs = qs.filter(user__email=email)
            except EmailAddress.DoesNotExist:
                return certification
        if qs.count() != 0:
            raise PermissionDenied({'custom': 'ALREADY_APPLIED_FOR_CERTIFICATION'})
        return certification
    except ExOCertification.DoesNotExist:
        raise PermissionDenied({'custom': 'NOT_ALLOWED_ACCESS_THIS_LEVEL'})


def trigger_payment(certification_request, country):
    auth_header = {'USERNAME': settings.AUTH_SECRET_KEY}
    user = certification_request.user
    contract_data = user.consultant.exo_profile.contracting_data

    payload = {
        'amount': certification_request.price,
        'currency': certification_request.cohort.currency.lower(),
        'concept': certification_request.cohort.invoice_concept,
        'detail': '',
        'email': user.email,
        'full_name': contract_data.name,
        'tax_id': contract_data.tax_id,
        'address': contract_data.address,
        'country': country.name,
        'country_code': country.code_2,
        'company_name': contract_data.company_name,
        'type_payment': settings.EXO_CERTIFICATION_PAYMENT_TYPE,
        'notes': '',
        'notify_webhook': '{}{}'.format(
            settings.EXOLEVER_HOST,
            reverse('api:exo-certification:webhooks-detail', kwargs={'pk': certification_request.pk}),
        ),
    }

    payment_uuid = None if not certification_request.payment_uuid else certification_request.payment_uuid
    base_url = get_root_payments_url() + settings.EXO_CERTIFICATION_PAYMENTS_API_URL

    try:
        if payment_uuid:
            response = requests.put(
                '{}/{}/'.format(base_url, payment_uuid),
                data=payload,
                headers=auth_header,
            )
        else:
            response = requests.post(
                base_url,
                data=payload,
                headers=auth_header,
            )
        logger.info('JoinPaymentSerializer {}'.format(response.content))
    except Exception as exc:
        logger.error('JoinPaymentSerializer {}'.format(str(exc)))
        return False

    data = response.json()
    certification_request.payment_uuid = data.get('paymentUuid')
    certification_request.payment_url = data.get('nextUrl')
    certification_request.save()


def update_certification_request(certification_request, data):
    country = data.get('country')

    certification_request.application_details = data.get('application_details', {})
    certification_request.cohort = data.get('cohort')
    certification_request.status = settings.EXO_CERTIFICATION_REQUEST_STATUS_CH_PENDING
    certification_request.save()

    # Checks whether the user is created or not
    if not certification_request.user:
        consultant = Consultant.objects.create_consultant(
            full_name=certification_request.requester_name,
            short_name=certification_request.requester_name,
            email=certification_request.requester_email,
            registration_process=True,
            skip_steps=[settings.REGISTRATION_STEPS_NAMES[1][0]],
            entry_point=get_entry_point_by_level(certification_request.level),
        )
        certification_request.user = consultant.user
        certification_request.save()

        category = settings.EXO_CERTIFICATION_INSTRUMENTATION_EVENTS.get(
            certification_request.level)
        coupon_code = certification_request.coupon.code if certification_request.coupon else None
        SegmentAnalytics.event(
            user=certification_request.user,
            category=category,
            event=settings.INSTRUMENTATION_EVENT_CERTIFICATION_INTERESTED,
            coupon=coupon_code,
            entry_point=settings.INSTRUMENTATION_USER_ENTRY_POINT_CERTIFICATIONS
        )
    elif not certification_request.user.is_consultant:
        Consultant.objects.create_consultant(
            full_name=certification_request.user.full_name,
            short_name=certification_request.user.short_name,
            email=certification_request.user.email,
            registration_process=True,
            skip_steps=[settings.REGISTRATION_STEPS_NAMES[1][0]],
            entry_point=get_entry_point_by_level(certification_request.level),
        )
        certification_request.refresh_from_db()

    contracting_data = {
        'name': data.get('billing_name'),
        'tax_id': data.get('tax_id'),
        'address': data.get('billing_address'),
        'company_name': data.get('company_name'),
    }
    user = certification_request.user
    user.consultant.exo_profile.set_contracting(**contracting_data)
    certification_request.price = certification_request.cohort.price
    if certification_request.coupon:
        certification_request.apply_coupon(certification_request.coupon, user)

    # Generates or updates payment
    trigger_payment(certification_request, country)

    certification_request.notify_referrer()

    category = settings.EXO_CERTIFICATION_INSTRUMENTATION_EVENTS.get(
        certification_request.level)
    SegmentAnalytics.event(
        user=certification_request.user,
        category=category,
        event=settings.INSTRUMENTATION_EVENT_CERTIFICATION_UPDATED,
        action_done=settings.INSTRUMENTATION_CERTIFICATION_ACTION_PROCEED_PAYMENT,
    )

    return certification_request

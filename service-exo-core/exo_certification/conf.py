import logging

from appconf import AppConf

from django.conf import settings  # noqa

logger = logging.getLogger(__name__)


class ExOCertificationConfig(AppConf):
    APP_NAME = 'exo_certification'

    # Certification Levels
    CERTIFICATION_CH_LEVEL_1 = 'L1'
    CERTIFICATION_CH_LEVEL_2 = 'L2'
    CERTIFICATION_CH_LEVEL_2A = 'L2A'
    CERTIFICATION_CH_LEVEL_3 = 'L3'
    CERTIFICATION_CH_LEVEL_DEFAULT = CERTIFICATION_CH_LEVEL_2

    CERTIFICATION_CH_LEVELS = (
        (CERTIFICATION_CH_LEVEL_1, 'ExO Foundations'),
        (CERTIFICATION_CH_LEVEL_2, 'ExO Consultant'),
        (CERTIFICATION_CH_LEVEL_2A, 'ExO Consultant Fastrack'),
        (CERTIFICATION_CH_LEVEL_3, 'ExO Sprint Coach'),
    )

    LEVEL_CH_1 = 'level_1'
    LEVEL_CH_2 = 'level_2'
    LEVEL_CH_3 = 'level_3'
    LEVEL_CH_2_FT = 'level_2_ft'
    LEVEL_CH_DEFAULT = LEVEL_CH_2

    LEVEL_CH_LEVELS = (
        (LEVEL_CH_1, 'L1'),
        (LEVEL_CH_2, 'L2'),
        (LEVEL_CH_2_FT, 'L2A'),
        (LEVEL_CH_3, 'L3'),
    )

    # CERTIFICATIONS EVENT vs LEVEL MAPPING
    INSTRUMENTATION_EVENTS = {
        CERTIFICATION_CH_LEVEL_1: 'Foundations',
        CERTIFICATION_CH_LEVEL_2: 'Consultant',
        CERTIFICATION_CH_LEVEL_2A: 'Consultant Fastrack',
        CERTIFICATION_CH_LEVEL_3: 'Sprint Coach',
    }

    COHORT_STATUS_CH_DRAFT = 'D'
    COHORT_STATUS_CH_OPEN = 'O'
    COHORT_STATUS_CH_CLOSED = 'C'
    COHORT_STATUS_CH_COMPLETED = 'F'
    COHORT_STATUS_CH_DEFAULT = COHORT_STATUS_CH_DRAFT

    COHORT_STATUS_CH_STATUSES = (
        (COHORT_STATUS_CH_DRAFT, 'Draft'),
        (COHORT_STATUS_CH_OPEN, 'Open'),
        (COHORT_STATUS_CH_CLOSED, 'Closed'),
        (COHORT_STATUS_CH_COMPLETED, 'Finished'),
    )

    # Cohort available languages
    COHORT_LANG_CH_EN = 'EN'
    COHORT_LANG_CH_ES = 'ES'
    COHORT_LANG_CH_DEFAULT = COHORT_LANG_CH_EN

    COHORT_CH_LANGS = (
        (COHORT_LANG_CH_EN, 'English'),
        (COHORT_LANG_CH_ES, 'Spanish'),
    )

    REQUEST_STATUS_CH_DRAFT = 'D'
    REQUEST_STATUS_CH_PENDING = 'P'
    REQUEST_STATUS_CH_APPROVED = 'A'
    REQUEST_STATUS_CH_FINISHED = 'F'
    REQUEST_STATUS_CH_CANCELLED = 'C'
    REQUEST_STATUS_CH_DEFAULT = REQUEST_STATUS_CH_DRAFT

    REQUEST_STATUS_CH_STATUSES = (
        (REQUEST_STATUS_CH_DRAFT, 'Draft'),
        (REQUEST_STATUS_CH_PENDING, 'Pending'),
        (REQUEST_STATUS_CH_APPROVED, 'Paid'),
        (REQUEST_STATUS_CH_FINISHED, 'Completed'),
        (REQUEST_STATUS_CH_CANCELLED, 'Cancelled'),
    )

    COUPON_TYPES_CH_PERCENT = 'P'
    COUPON_TYPES_CH_AMOUNT = 'A'
    COUPON_TYPES_CH_DEFAULT = COUPON_TYPES_CH_AMOUNT

    COUPON_CH_TYPES = (
        (COUPON_TYPES_CH_AMOUNT, 'Fixed Amount'),
        (COUPON_TYPES_CH_PERCENT, 'Percent'),
    )

    CURRENCY_CH_EURO = 'EUR'
    CURRENCY_CH_DOLLAR = 'USD'
    CURRENCY_CH_STERLING = 'GBP'
    CURRENCY_CH_DEFAULT = CURRENCY_CH_EURO

    CURRENCY_CH_CURRENCIES = (
        (CURRENCY_CH_EURO, 'EURO'),
        (CURRENCY_CH_DOLLAR, 'Dollar'),
        (CURRENCY_CH_STERLING, 'Pound Sterling'),
    )

    PRICES = {
        LEVEL_CH_2: 1500,
        LEVEL_CH_2_FT: 500,
        LEVEL_CH_3: 2500,
    }

    PAYMENTS_API_URL = 'api/payment/'
    PAYMENT_TYPE = 'C'

    # HS Entry Points
    EP_FORM_EXO_CONSULTANT = 'CERTIFICATION_LEVEL_2_FORM'
    EP_FORM_EXO_CONSULTANT_FT = 'CERTIFICATION_LEVEL_2_FT'
    EP_FORM_EXO_SPRINT_COACH = 'CERTIFICATION_LEVEL_2_FORM'

    LEVELS_EP_MAPPING = {
        LEVEL_CH_2: EP_FORM_EXO_CONSULTANT,
        LEVEL_CH_2_FT: EP_FORM_EXO_CONSULTANT_FT,
        LEVEL_CH_3: EP_FORM_EXO_SPRINT_COACH,
    }

    # HS Pipelines
    HS_PIPELINE_ID = 'certification_pipeline'
    HS_STAGE_INTERESTED = 'cert_interested'
    HS_STAGE_PROCEED_PAYMENT = 'cert_proced_payment'
    HS_STAGE_PAYMENT_RECEIVED = 'cert_payment_received'
    HS_STAGE_CERTIFICATION_ISSUED = 'cert_certification_sent'

    HS_LEVEL_DEAL_MAPPING = {
        CERTIFICATION_CH_LEVEL_2: 'level_2',
        CERTIFICATION_CH_LEVEL_2A: 'level_2_ft',
        CERTIFICATION_CH_LEVEL_3: 'level_3',
    }

    # Metrics

    METRIC_ACTION_PAY = 'pay'
    METRIC_ACTION_ACQUIRE = 'acquire'
    METRIC_ACTION_LIST = (
        (METRIC_ACTION_PAY, 'Customer'),
        (METRIC_ACTION_ACQUIRE, 'Certification'),
    )

    METRIC_LABEL_PREFIX = {
        METRIC_ACTION_PAY: 'certification_paid_{}',
        METRIC_ACTION_ACQUIRE: 'certification_granted_{}',
    }

    METRIC_LABELS = {
        LEVEL_CH_1: 'exo_foundations',
        LEVEL_CH_2: 'exo_consultant',
        LEVEL_CH_2_FT: 'exo_fastrack',
        LEVEL_CH_3: 'exo_sprint_coach',
    }

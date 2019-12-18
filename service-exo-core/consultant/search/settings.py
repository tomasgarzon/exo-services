from django.conf import settings
from django.utils.text import slugify


class ConsultantSettings:
    CH_CERTIFIED = 'Active'
    CH_DISABLED = 'Disabled'

    SLUG_REGISTRATION_STEP_SIGNUP = slugify(settings.REGISTRATION_STEP_SIGNUP)
    SLUG_REGISTRATION_STEP_AGREEMENT = slugify(settings.REGISTRATION_STEP_AGREEMENT)
    SLUG_REGISTRATION_STEP_PROFILE = slugify(settings.REGISTRATION_STEP_PROFILE)

    CONSULTANT_CH_STATUS = (
        (SLUG_REGISTRATION_STEP_SIGNUP, 'Sign Up sent'),
        (SLUG_REGISTRATION_STEP_AGREEMENT, 'Agreement'),
        (SLUG_REGISTRATION_STEP_PROFILE, 'Onboarding'),
        (CH_CERTIFIED, 'Active'),
        (CH_DISABLED, 'Disabled'),
    )

    CH_STATUS_STAFF_ACTIVE = 'A'
    CH_STATUS_STAFF_PENDING = 'P'
    CH_STATUS_STAFF_INACTIVE = 'D'
    CH_STATUS_STAFF_CERTIFIED = 'C'
    CONSULTANT_CH_STATUS_STAFF = (
        (CH_STATUS_STAFF_ACTIVE, 'Active'),
        (CH_STATUS_STAFF_PENDING, 'Pending'),
        (CH_STATUS_STAFF_INACTIVE, 'Inactive'),
        (CH_STATUS_STAFF_CERTIFIED, 'Certified'),
    )

    CH_MTP = 'MTP'


consultant_settings = ConsultantSettings()

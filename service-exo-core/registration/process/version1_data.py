from django.conf import settings

from ..models import registration_process_template, ProcessTemplateStepOption


STEPS_NAMES = settings.REGISTRATION_STEPS_NAMES

EMAIL_TPL_DATA = {
    STEPS_NAMES[0][1]: {
        'email_ok': 'registration_step_accept',
        'email_ok_subject': '%(user_from.full_name)s signed ExO Agreement',
        'email_ok_body': '%(user_from.email)s has already signed the ExO Agreement.',
        'email_ko': 'registration_step_decline',
        'email_ko_subject': '',
        'email_ko_body': '',
    },
    STEPS_NAMES[1][1]: {
        'email_ok': 'registration_step_accept',
        'email_ok_subject': '%(user_from.full_name)s filled Skills Assessment',
        'email_ok_body': '%(user_from.full_name)s (%(user_from.email)s) has filled Skills Assessment',
        'email_ko': '',
        'email_ko_subject': '',
        'email_ko_body': '',
    },
    STEPS_NAMES[2][1]: {
        'email_ok': 'registration_step_accept',
        'email_ok_subject': '%(user_from.full_name)s signed up into ' + settings.BRAND_NAME,
        'email_ok_body': '%(user_from.full_name)s (%(user_from.email)s) has signed up into ' + settings.BRAND_NAME,
        'email_ko': '',
        'email_ko_subject': '',
        'email_ko_body': '',
    },
    STEPS_NAMES[3][1]: {
        'email_ok': 'registration_step_accept',
        'email_ok_subject': '%(user_from.full_name)s filled Welcome Onboarding',
        'email_ok_body': '%(user_from.full_name)s (%(user_from.email)s) has filled Welcome Onboarding',
        'email_ko': '',
        'email_ko_subject': '',
        'email_ko_body': '',
    },
}


def get_email_tpl_data(name):
    new_email_tpl = registration_process_template.NotificationStep()
    data = EMAIL_TPL_DATA.get(name)

    new_email_tpl.email_ok = data.get('email_ok')
    new_email_tpl.email_ok_subject = data.get('email_ok_subject')
    new_email_tpl.email_ok_body = data.get('email_ok_body')

    new_email_tpl.email_ko = data.get('email_ko')
    new_email_tpl.email_ko_subject = data.get('email_ko_subject')
    new_email_tpl.email_ko_body = data.get('email_ko_body')

    return new_email_tpl


def generate_step_options():
    options = {}

    new_option = ProcessTemplateStepOption()
    new_option.name = 'Send admin email'
    new_option.description = 'Send notification email by default to RegistrationManager'
    new_option.customizable = False
    new_option.pre_step = False
    new_option.post_step = True
    new_option.property_name = settings.REGISTRATION_OPTION_SEND_ADMIN_EMAIL
    new_option.property_value = True
    options['send_admin_email_by_default__true'] = new_option

    new_option = ProcessTemplateStepOption()
    new_option.name = 'Send admin email'
    new_option.description = 'Send notification email by default to RegistrationManager'
    new_option.customizable = False
    new_option.pre_step = False
    new_option.post_step = True
    new_option.property_name = settings.REGISTRATION_OPTION_SEND_ADMIN_EMAIL
    new_option.property_value = False
    options['send_admin_email_by_default__false'] = new_option

    new_option = ProcessTemplateStepOption()
    new_option.name = 'Send user email'
    new_option.description = 'Send Consultant email by default with step information'
    new_option.customizable = True
    new_option.pre_step = False
    new_option.post_step = True
    new_option.property_name = settings.REGISTRATION_OPTION_SEND_USER_EMAIL
    new_option.property_value = False
    options['send_user_email_by_default__false'] = new_option

    new_option = ProcessTemplateStepOption()
    new_option.name = 'Send user email'
    new_option.description = 'Send Consultant email by default with step information'
    new_option.customizable = True
    new_option.pre_step = False
    new_option.post_step = True
    new_option.property_name = settings.REGISTRATION_OPTION_SEND_USER_EMAIL
    new_option.property_value = True
    options['send_user_email_by_default__true'] = new_option

    new_option = ProcessTemplateStepOption()
    new_option.name = 'Public log'
    new_option.description = 'Configure visible log for users'
    new_option.customizable = True
    new_option.pre_step = False
    new_option.post_step = True
    new_option.property_name = settings.REGISTRATION_OPTION_PUBLIC_LOG_VIEW
    new_option.property_value = None
    new_option.property_values = settings.CONSULTANT_VALIDATION_STATUS_PUBLIC_LOG
    options['public_log_view'] = new_option

    for key, value in options.items():
        value.save()
    return options

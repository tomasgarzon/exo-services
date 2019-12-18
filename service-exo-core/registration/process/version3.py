from django.conf import settings

from ..models import registration_process_template
from .version1_data import (
    generate_step_options,
    get_email_tpl_data
)

STEPS_NAMES = settings.REGISTRATION_STEPS_NAMES


def create_process_template_v3():

    step_options = generate_step_options()

    template, _ = registration_process_template.RegistrationProcessTemplate.objects.get_or_create(
        name='Registration v3',
        version=3,
    )

    step1 = registration_process_template.ProcessTemplateStep(
        template=template,
        name=STEPS_NAMES[2][1],
        code=STEPS_NAMES[2][0],
        action=settings.CONSULTANT_VALIDATION_USER,
    )
    notification_step = get_email_tpl_data(STEPS_NAMES[2][1])
    notification_step.save()
    step1.email_tpl = notification_step
    step1.save()
    options = [
        step_options.get('send_admin_email_by_default__false'),
        step_options.get('send_user_email_by_default__true'),
        step_options.get('public_log_view'),
    ]
    for opt in options:
        step1.options.add(opt)

    step2 = registration_process_template.ProcessTemplateStep(
        template=template,
        name=STEPS_NAMES[0][1],
        code=STEPS_NAMES[0][0],
        action=settings.CONSULTANT_VALIDATION_AGREEMENT,
    )
    notification_step = get_email_tpl_data(STEPS_NAMES[0][1])
    notification_step.save()
    step2.email_tpl = notification_step
    step2.save()

    options = [
        step_options.get('send_admin_email_by_default__false'),
        step_options.get('send_user_email_by_default__false'),
        step_options.get('public_log_view'),
    ]
    for opt in options:
        step2.options.add(opt)

    step3 = registration_process_template.ProcessTemplateStep(
        template=template,
        name=STEPS_NAMES[3][1],
        code=STEPS_NAMES[3][0],
        action=settings.CONSULTANT_VALIDATION_BASIC_PROFILE,
    )
    notification_step = get_email_tpl_data(STEPS_NAMES[3][1])
    notification_step.save()
    step3.email_tpl = notification_step
    step3.save()

    options = [
        step_options.get('send_admin_email_by_default__false'),
        step_options.get('send_user_email_by_default__false'),
        step_options.get('public_log_view'),
    ]
    for opt in options:
        step3.options.add(opt)

    step1.next_steps.add(step2)
    step2.next_steps.add(step3)
    step2.previous_steps.add(step1)
    step3.previous_steps.add(step2)
    return template

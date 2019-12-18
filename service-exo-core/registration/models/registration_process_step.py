from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.apps import apps

import logging
from model_utils.models import TimeStampedModel

from utils.descriptors import ChoicesDescriptorMixin

from .registration_step_option import StepOption
from .registration_process_step_email_mixin import ProcessStepEmailMixin
from ..exceptions import ProcessStepException
from ..conf import settings


logger = logging.getLogger('registration_process')


class ProcessStep(
        ChoicesDescriptorMixin,
        ProcessStepEmailMixin,
        TimeStampedModel):
    process = models.ForeignKey(
        'RegistrationProcess',
        related_name='steps',
        on_delete=models.CASCADE)
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE,
        blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey(
        'content_type', 'object_id')
    code = models.CharField(
        max_length=100,
        blank=True, null=True)
    next_steps = models.ManyToManyField('self', symmetrical=False)
    options = models.ManyToManyField('StepOption')
    status = models.CharField(
        max_length=1,
        choices=settings.REGISTRATION_CH_STEP_STATUS,
        default=settings.REGISTRATION_CH_STEP_STATUS_DEFAULT,
    )

    class Meta:
        ordering = ['id']

    def __str__(self):
        validation_object = ''
        if self.content_object:
            validation_object = self.content_object.get_name_display()
        return '{} {}'.format(
            validation_object,
            self.get_status_display(),
        ).capitalize()

    @classmethod
    def create_step(
        cls, process, user, owner, user_from,
        template_step, next_steps=[],
    ):
        process_step = ProcessStep(process=process)
        process_step.code = template_step.code
        process_step.content_object = None
        process_step.save()
        for opt in template_step.options.all():
            if opt.customizable:
                new_opt = StepOption.reset(opt)
                process_step.options.add(new_opt)
        return process_step

    @property
    def invitation(self):
        invitation = None
        Invitation = apps.get_model(
            app_label='invitation',
            model_name='Invitation',
        )
        try:
            if self.content_object:
                invitation = Invitation.objects.filter_by_object(
                    self.content_object,
                ).get()
        except Invitation.DoesNotExist:
            pass

        return invitation

    @property
    def public_url(self):
        """
        Get the URL for this step
        """
        public_url = self.content_object.get_public_url(self.invitation)

        return public_url

    def check_option(self, option, *args, **kwargs):
        """
        To check and option with multiple values:
            object.check_option(option_name, value='value_to_check')

        Check an option for this step
            - First check as local step option
            - If not exist check as TemplateStep option
            - If not exist neither return None
        """
        result = None
        option_to_check = None
        is_method = False

        for opt in self.options.all():
            if opt.method_name == option or opt.property_name == option:
                is_method = opt.method_name is not None
                option_to_check = opt
                break

        if not option_to_check:
            for template_option in self.process.get_template_step_by_code(self.code).options.all():
                if template_option.method_name == option or template_option.property_name == option:
                    is_method = template_option.method_name is not None
                    option_to_check = template_option
                    break

        if option_to_check:
            if not is_method:
                if option_to_check.property_value is not None:
                    result = option_to_check.property_value

                elif option_to_check.property_values is not None or \
                        option_to_check.property_values == []:

                    value_to_check = kwargs.get('value', None)
                    if value_to_check is None:
                        raise ProcessStepException(
                            'You have to supply a value to compare with',
                        )
                    result = value_to_check in option_to_check.property_values

            else:
                raise NotImplementedError

        return result

    def start(
        self, user, owner, user_from,
        template_step, custom_text=None, autosend=None,
    ):
        """
        Initialize this step and mark as "current"
        """
        logger.info('Step started: {}'.format(template_step.code))
        self.status = settings.REGISTRATION_CH_CURRENT
        if autosend is None:
            autosend = self.check_option(
                settings.REGISTRATION_OPTION_SEND_USER_EMAIL,
            )

        validation_type = template_step.action
        validation_status_object = user.consultant.add_validation(
            user_from or user,
            validation_type,
            custom_text=custom_text,
            autosend=autosend,
        )

        self.content_object = validation_status_object
        self.save()

    def executed(self, template_step, user_from, *args, **kwargs):
        logger.info('Step executed: {}'.format(template_step.code))
        self.status = settings.REGISTRATION_CH_EXECUTED
        self.save()
        if template_step.email_tpl.email_ok:
            self._send_email_step_ok(
                template=template_step,
                user_from=self.content_object.consultant.user,
                *args, **kwargs
            )

    def cancel(self, template_step, user_from, *args, **kwargs):
        self.status = settings.REGISTRATION_CH_CANCEL
        self.save()
        if template_step.email_tpl.email_ko:
            self._send_email_step_ko(
                template=template_step,
                user_from=self.content_object.consultant.user,
                *args, **kwargs
            )

        self.content_object = None

    def _reactivate_step(self):
        """
        Reactivate a cancelled step to continue the Registration Process
        """
        if self.is_declined:
            self.status = settings.REGISTRATION_CH_STEP_STATUS_REACTIVATED
            self.save()

import logging

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.contrib.postgres.fields import JSONField

from model_utils.models import TimeStampedModel
from rest_framework.status import HTTP_400_BAD_REQUEST

from consultant.hubspot.contact import DEFAULT_ON_BOARDING_ENTRY_POINT
from utils.drf.exceptions import ObjectDuplicated
from utils.models import CreatedByMixin

from .registration_process_template import RegistrationProcessTemplate
from ..conf import settings
from ..querysets.registration_process import RegistrationProcessQuerySet
from .registration_process_step import ProcessStep
from .log import RegistrationLog


logger = logging.getLogger('registration_process')


class RegistrationProcess(CreatedByMixin, TimeStampedModel):

    template = models.ForeignKey(
        'RegistrationProcessTemplate',
        on_delete=models.CASCADE)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name='registration_process',
        on_delete=models.CASCADE)
    entry_point = JSONField(blank=True, null=True)
    objects = RegistrationProcessQuerySet.as_manager()

    def __str__(self):
        return 'User id: {}'.format(self.user.id)

    @property
    def owner(self):
        return self.user

    @property
    def user_from(self):
        return self.created_by

    @property
    def consultant(self):
        return self.user.consultant

    @property
    def is_registered(self):
        cond1 = self.last_step and self.last_step.code == self.template.last_step.code
        return cond1 and self.last_step.is_executed

    @property
    def current_step(self):
        return self.steps.filter(
            status=settings.REGISTRATION_CH_CURRENT).first()

    @property
    def last_step(self):
        return self.steps.last()

    @property
    def real_entry_point(self):
        entry_point_obj = self.entry_point or {}
        entry_point = entry_point_obj.get(
            'name',
            DEFAULT_ON_BOARDING_ENTRY_POINT
        )

        return entry_point

    def resume(self):
        # continue the process from last step executed
        current = self.steps.filter(status=settings.REGISTRATION_CH_CANCEL).first()
        if current:
            current.status = settings.REGISTRATION_CH_CURRENT
            current.save()

    def check_option(self, option, step=None, *args, **kwargs):
        option_result = None
        opts = {}
        value = kwargs.get('value', None)
        step_to_check = self.current_step
        if step:
            step_to_check = step

        if step_to_check:
            if value is not None:
                opts['value'] = value
            option_result = step_to_check.check_option(
                option,
                **opts
            )

        return option_result

    def get_next_step_public_url(self):
        public_url = None
        if self.current_step and not self.is_registered:
            public_url = self.current_step.public_url

        return public_url

    def get_template_step_by_code(self, code):
        return self.template.steps.filter(code=code).first()

    def get_step_by_code(self, code):
        return self.steps.filter(code=code).first()

    def get_step_for_object(self, step_related_object):
        """
        Return the Step related with this RegistrationProcess and the Invitation
        object for the Step
        """
        if step_related_object is None:
            return None
        step = self.steps.filter(
            object_id=step_related_object.id,
            content_type_id=ContentType.objects.get_for_model(step_related_object).id).first()

        if not step:
            for template_stp, process_step in zip(self.template.steps.all(), self.steps.all()):
                if not hasattr(step_related_object, 'validation'):
                    continue
                if template_stp.action == step_related_object.validation.name:
                    if process_step.is_pending or process_step.is_declined:
                        step = process_step
                        break

        return step

    def _store_log(
        self, text, status=None, display_status=None,
        related_object=None, display=None,
    ):
        new_log = RegistrationLog(process=self)
        step = self.get_step_for_object(related_object)
        opt_params = {'value': status}
        if display is None and step is not None:
            new_log.display = self.check_option(
                'public_log_view',
                step,
                **opt_params
            )
        else:
            new_log.display = display

        if related_object:
            new_log.content_object = related_object
        new_log.display = new_log.display if new_log.display is not None else False
        new_log.text = text
        new_log.status = status
        new_log.display_status = display_status
        new_log.save()

    def _start_step(self, step, user_from, custom_text=None):
        """
            Create object for the next RegistrationProcess Step
        """
        step.start(
            self.user,
            self.created_by,
            user_from,
            self.template.get_step_by_code(step.code),
            custom_text,
        )

    def execute_step(self, user_from, step_code):
        step = self.get_step_by_code(step_code)
        template_step = self.template.get_step_by_code(step.code)

        step.executed(template_step, user_from)
        for next_step in step.next_steps.all():
            code = next_step.code
            template_step_next = self.template.get_step_by_code(code)
            next_step.start(
                self.user,
                self.created_by,
                user_from,
                template_step_next,
            )

    def cancel_step(self, user_from, step_code, description=None):
        current_step = self.get_step_by_code(step_code)
        template_step = self.template.get_step_by_code(current_step.code)

        current_step.cancel(
            template_step,
            user_from,
            description=description,
        )
        template_step_next = None
        for next_step in self.steps.all():
            code = next_step.code
            if step_code in next_step.next_steps.all().values_list('code', flat=True):
                template_step_next = self.template.get_step_by_code(code)
                next_step.start(
                    self.user,
                    self.created_by,
                    user_from,
                    template_step_next,
                    autosend=False,
                )
        if not template_step_next:
            current_step.start(
                self.user,
                self.created_by,
                user_from,
                template_step,
                autosend=False,
            )

    def start(self, user_from, custom_text=None):
        # Look for the first step with Pending status
        step = self.steps.filter(status=settings.REGISTRATION_CH_PENDING).first()

        self._start_step(
            step=step,
            user_from=user_from,
            custom_text=custom_text,
        )

    @classmethod
    def _create_process(
        cls, user_from, user, custom_text=None,
        auto_start=True, process_template=None, skip_steps=[],
        entry_point=None,
    ):
        """
        Create Registration Process
        """
        if not process_template:
            process_template = RegistrationProcessTemplate.objects.first()
        process = cls(
            template=process_template,
            user=user,
            created_by=user_from,
            entry_point=entry_point,
        )
        process.save()
        logger.info('Creating process for: {}'.format(user))
        previous_step = None
        # Create all Steps for process
        for template_step in process_template.steps.all():
            # Steps skipped
            if template_step.code in skip_steps:
                continue
            logger.info('Add step: {}'.format(template_step.code))
            step = ProcessStep.create_step(
                process=process,
                user=process.user,
                owner=process.owner,
                user_from=user_from,
                template_step=template_step,
            )
            if previous_step:
                previous_step.next_steps.add(step)
            previous_step = step

        if auto_start:
            process.start(user_from, custom_text)

        return process

    @classmethod
    def create_process(
        cls, user_from, user,
        custom_text=None, version=None, skip_steps=[],
        entry_point=None,
    ):
        cp_tpl = RegistrationProcessTemplate.objects.first()
        if version:
            try:
                cp_tpl = RegistrationProcessTemplate.objects.get(
                    version=version,
                )
            except RegistrationProcessTemplate.DoesNotExist:
                return None

        previous = cls.objects.filter(
            template=cp_tpl,
            user=user,
        ).count()
        if previous > 0:
            raise ObjectDuplicated(
                detail='Registration process already started.',
                status_code=HTTP_400_BAD_REQUEST,
            )
        return cls._create_process(
            user_from=user_from,
            user=user,
            process_template=cp_tpl,
            custom_text=custom_text,
            skip_steps=skip_steps,
            entry_point=entry_point,
        )
